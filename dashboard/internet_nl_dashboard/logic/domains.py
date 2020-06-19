import logging
import re
from typing import Any, Dict, List, Tuple

import tldextract
from actstream import action
from constance import config
from django.db.models import Count, Prefetch
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint
from websecmap.scanners.scanner.dns_endpoints import compose_discover_task

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan, UrlList,
                                                    UrlListReport)
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import (initialize_scan,
                                                                                   update_state)

log = logging.getLogger(__package__)


# todo: write test
def alter_url_in_urllist(account, data) -> Dict[str, Any]:
    # data = {'list_id': list.id, 'url_id': url.id, 'new_url_string': url.url}

    expected_keys = ['list_id', 'url_id', 'new_url_string']
    if check_keys(expected_keys, data):
        return operation_response(error=True, message="Missing keys in data.")

    # what was the old id we're changing?
    old_url = Url.objects.all().filter(pk=data['url_id']).first()
    if not old_url:
        return operation_response(error=True, message="The old url does not exist.")

    if old_url.url == data['new_url_string']:
        # no changes
        return operation_response(success=True, message="Saved.")

    # is this really a list?
    urllist = UrlList.objects.all().filter(account=account, pk=data['list_id']).first()
    if not urllist:
        return operation_response(error=True, message="List does not exist.")

    # is the url valid?
    if not Url.is_valid_url(data['new_url_string']):
        return operation_response(error=True, message="New url does not have the correct format.")

    # fetch the url, or create it if it doesn't exist.
    new_url, created = get_url(data['new_url_string'])

    # don't throw away the url, only from the list. (don't call delete, as it will delete the record)
    urllist.urls.remove(old_url)
    # Save after deletion, in case the same url is added it will not cause a foreign key error.
    urllist.save()

    urllist.urls.add(new_url)
    urllist.save()

    # somewhat inefficient to do 4 queries, yet, good enough
    old_url_has_mail_endpoint = Endpoint.objects.all().filter(url=old_url, is_dead=False, protocol='dns_soa').exists()
    old_url_has_web_endpoint = Endpoint.objects.all().filter(url=old_url, is_dead=False, protocol='dns_a_aaa').exists()

    if not created:
        new_url_has_mail_endpoint = Endpoint.objects.all().filter(
            url=new_url, is_dead=False, protocol='dns_soa').exists()
        new_url_has_web_endpoint = Endpoint.objects.all().filter(
            url=new_url, is_dead=False, protocol='dns_a_aaa').exists()
    else:
        new_url_has_mail_endpoint = 'unknown'
        new_url_has_web_endpoint = 'unknown'

    new_fragments = tldextract.extract(new_url.url)
    old_fragments = tldextract.extract(old_url.url)

    return operation_response(success=True, message="Saved.", data={
        'created': {'id': new_url.id, 'url': new_url.url, 'created_on': new_url.created_on,
                    'has_mail_endpoint': new_url_has_mail_endpoint,
                    'has_web_endpoint': new_url_has_web_endpoint, 'subdomain': new_fragments.subdomain,
                    'domain': new_fragments.domain, 'suffix': new_fragments.suffix},
        'removed': {'id': old_url.id, 'url': old_url.url, 'created_on': old_url.created_on,
                    'has_mail_endpoint': old_url_has_mail_endpoint,
                    'has_web_endpoint': old_url_has_web_endpoint, 'subdomain': old_fragments.subdomain,
                    'domain': old_fragments.domain, 'suffix': old_fragments.suffix},
    })


def scan_now(account, user_input) -> Dict[str, Any]:
    urllist = UrlList.objects.all().filter(
        account=account, id=user_input.get('id', -1), is_deleted=False).annotate(num_urls=Count('urls')).first()

    if not urllist:
        return operation_response(error=True, message="List could not be found.")

    if not urllist.is_scan_now_available():
        return operation_response(error=True, message="Not all conditions for initiating a scan are met.")

    # make sure there are no errors on this list:
    max_urls = config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST
    if urllist.num_urls > max_urls:
        return operation_response(error=True, message=f"Cannot scan: Amount of urls exceeds the maximum of {max_urls}.")

    if not account.connect_to_internet_nl_api(account.internet_nl_api_username, account.decrypt_password()):
        return operation_response(error=True, message=f"Credentials for the internet.nl API are not valid.")

    # Make sure the fernet key is working fine, you are on the correct queue (-Q storage) and that the correct API
    # version is used.
    # Run this before updating the list, as this might go wrong for many reasons.
    initialize_scan(urllist, manual_or_scheduled="manual")

    # done: have to update the list info. On the other hand: there is no guarantee that this task already has started
    # ...to fix this issue, we'll use a 'last_manual_scan' field.
    urllist.last_manual_scan = timezone.now()
    urllist.save()

    return operation_response(success=True, message="Scan started")


def scan_urllist_now_ignoring_business_rules(urllist: UrlList):
    urllist = UrlList.objects.all().filter(pk=urllist.id).first()

    if not urllist:
        return operation_response(error=True, message="List could not be found.")

    initialize_scan(urllist)

    urllist.last_manual_scan = timezone.now()
    urllist.save()

    return operation_response(success=True, message="Scan started")


def get_url(new_url_string: str):

    # first check if one exists, if not, create it.
    url = Url.objects.all().filter(url=new_url_string).first()
    if url:
        return url, False

    url = Url.add(new_url_string)
    return url, True


def create_list(account: Account, user_input: Dict) -> Dict[str, Any]:
    expected_keys = ['id', 'name', 'enable_scans', 'scan_type', 'automated_scan_frequency', 'scheduled_next_scan']
    if sorted(user_input.keys()) != sorted(expected_keys):
        return operation_response(error=True, message="Missing settings.")

    frequency = validate_list_automated_scan_frequency(user_input['automated_scan_frequency'])
    data = {
        'account': account,
        'name': validate_list_name(user_input['name']),
        'enable_scans': bool(user_input['enable_scans']),
        'scan_type': validate_list_scan_type(user_input['scan_type']),
        'automated_scan_frequency': frequency,
        'scheduled_next_scan': UrlList.determine_next_scan_moment(frequency),
    }

    urllist = UrlList(**data)
    urllist.save()

    # make sure the account is serializable.
    data['account'] = account.id

    # adding the ID makes it possible to add new urls to a new list.
    data['id'] = urllist.pk

    # empty list, no warnings.
    data['list_warnings'] = []

    # give a hint if it can be scanned:
    data['scan_now_available'] = urllist.is_scan_now_available()

    # Sprinkling an activity stream action.
    action.send(account, verb='created list', target=urllist, public=False)

    return operation_response(success=True, message="List created.", data=data)


def delete_list(account: Account, user_input: dict):
    """
    The first assumption was that a list is not precious or special, and that it can be quickly re-created with an
    import from excel or a csv paste in the web interface. Yet this assumption is wrong. It's valuable to keep the list
    also after it is deleted. This gives insight into what scans have happened in the past on what list.

    To do that, the is_deleted columns have been introduced.

    :param account:
    :param user_input:
    :return:
    """
    urllist = UrlList.objects.all().filter(account=account, id=user_input.get('id', -1), is_deleted=False).first()
    if not urllist:
        return operation_response(error=True, message="List could not be deleted.")

    urllist.is_deleted = True
    urllist.enable_scans = False
    urllist.deleted_on = timezone.now()
    urllist.save()

    # Sprinkling an activity stream action.
    action.send(account, verb='deleted list', target=urllist, public=False)

    return operation_response(success=True, message="List deleted.")


def get_scan_status_of_list(account: Account, list_id: int) -> Dict[str, Any]:
    """
    Gets the latest report and the scanning status of a list, this is meant as a small status monitor per list.
    This updates the "can scan" buttons and updates the link to the latest report. It does not propagate user changes.

    :param account:
    :param list_id:
    :return:
    """

    prefetch_last_scan = Prefetch(
        'accountinternetnlscan_set',
        queryset=AccountInternetNLScan.objects.order_by('-id').select_related('scan').only('scan_id',
                                                                                           'finished_on'),
        to_attr='last_scan'
    )

    last_report_prefetch = Prefetch(
        'urllistreport_set',
        # filter(pk=UrlListReport.objects.latest('id').pk).
        queryset=UrlListReport.objects.order_by('-id').only('id', 'at_when'),
        to_attr='last_report'
    )

    urllist = UrlList.objects.all().filter(
        account=account,
        id=list_id,
        is_deleted=False
    ).prefetch_related(prefetch_last_scan, last_report_prefetch).first()

    if not urllist:
        return {}

    data = {}
    data['last_scan_id'] = None if not len(urllist.last_scan) else urllist.last_scan[0].scan.id
    data['last_scan_finished'] = None if not len(urllist.last_scan) else urllist.last_scan[0].finished
    data['last_report_id'] = None if not len(urllist.last_report) else urllist.last_report[0].id
    data['last_report_date'] = None if not len(urllist.last_report) else urllist.last_report[0].at_when
    data['scan_now_available'] = urllist.is_scan_now_available()

    return data


def cancel_scan(account, scan_id: int):
    """
    :param account: Account
    :param scan_id: AccountInternetNLScan ID
    :return:
    """

    scan = AccountInternetNLScan.objects.all().filter(account=account, pk=scan_id).first()

    if not scan:
        return operation_response(error=True, message="scan not found")

    if scan.state == 'finished':
        return operation_response(success=True, message="scan already finished")

    if scan.state == 'cancelled':
        return operation_response(success=True, message="scan already cancelled")

    scan.finished_on = timezone.now()
    scan.save()
    update_state("cancelled", scan)

    # Sprinkling an activity stream action.
    action.send(account, verb='cancelled scan', target=scan, public=False)

    return operation_response(success=True, message="scan cancelled")


# @pysnooper.snoop()
def update_list_settings(account: Account, user_input: Dict) -> Dict[str, Any]:
    """

    This cannot update the urls, as that would increase complexity too much.

    :param account:
    :param user_input: {
        'id': int,
        'name': str,
        'enable_scans': bool,
        'scan_type': str,

        # todo: Who should set this? Should this be set by admins? How can we avoid permission hell?
        # Probably as long as the settings are not too detailed / too frequently.
        'automated_scan_frequency': str,
    }
    :return:
    """

    expected_keys = ['id', 'name', 'enable_scans', 'scan_type', 'automated_scan_frequency', 'scheduled_next_scan']
    if check_keys(expected_keys, user_input):
        return operation_response(error=True, message="Missing settings.")

    prefetch_last_scan = Prefetch(
        'accountinternetnlscan_set',
        queryset=AccountInternetNLScan.objects.order_by('-id').select_related('scan'),
        to_attr='last_scan'
    )

    last_report_prefetch = Prefetch(
        'urllistreport_set',
        # filter(pk=UrlListReport.objects.latest('id').pk).
        queryset=UrlListReport.objects.order_by('-id').only('id', 'at_when'),
        to_attr='last_report'
    )

    urllist = UrlList.objects.all().filter(
        account=account,
        id=user_input['id'],
        is_deleted=False
    ).annotate(num_urls=Count('urls')).prefetch_related(prefetch_last_scan, last_report_prefetch).first()

    if not urllist:
        return operation_response(error=True, message="No list of urls found.")

    # Yes, you can try and set any value. Values that are not recognized do not result in errors / error messages,
    # instead they will be overwritten with the default. This means less interaction with users / less annoyance over
    # errors on such simple forms.
    frequency = validate_list_automated_scan_frequency(user_input['automated_scan_frequency'])
    data = {
        'id': urllist.id,
        'account': account,
        'name': validate_list_name(user_input['name']),
        'enable_scans': bool(user_input['enable_scans']),
        'scan_type': validate_list_scan_type(user_input['scan_type']),
        'automated_scan_frequency': frequency,
        'scheduled_next_scan': UrlList.determine_next_scan_moment(frequency),
    }

    updated_urllist = UrlList(**data)
    updated_urllist.save()

    # make sure the account is serializable.
    data['account'] = account.id
    data['num_urls'] = urllist.num_urls

    # inject the last scan information.
    data['last_scan_id'] = None if not len(urllist.last_scan) else urllist.last_scan[0].scan.id

    data['last_scan'] = None if not len(urllist.last_scan) else urllist.last_scan[0].started_on.isoformat()
    data['last_scan_finished'] = None if not len(urllist.last_scan) else urllist.last_scan[0].finished
    data['last_report_id'] = None if not len(urllist.last_report) else urllist.last_report[0].id
    data['last_report_date'] = None if not len(urllist.last_report) else urllist.last_report[0].at_when

    data['scan_now_available'] = updated_urllist.is_scan_now_available()

    # list warnings (might do: make more generic, only if another list warning ever could occur.)
    list_warnings = []
    if urllist.num_urls > config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST:
        list_warnings.append('WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED')
    data['list_warnings'] = []

    log.debug(data)

    # Sprinkling an activity stream action.
    action.send(account, verb='updated list', target=updated_urllist, public=False)

    return operation_response(success=True, message="Updated list settings", data=data)


def check_keys(expected_keys, object):
    if sorted(object.keys()) != sorted(expected_keys):
        return False


def validate_list_name(list_name):
    return list_name[0:120]


# todo: this can be a generic tuple check.
def validate_list_automated_scan_frequency(automated_scan_frequency):
    if (automated_scan_frequency, automated_scan_frequency) not in \
            UrlList._meta.get_field('automated_scan_frequency').choices:
        return UrlList._meta.get_field('automated_scan_frequency').default
    return automated_scan_frequency


def validate_list_scan_type(scan_type):
    # if the option doesn't exist, return the first option as the fallback / default.
    if (scan_type, scan_type) not in UrlList._meta.get_field('scan_type').choices:
        return UrlList._meta.get_field('scan_type').default
    return scan_type


def rename_list(account: Account, list_id: int, new_name: str) -> bool:
    # Existing list name: no problem.
    # List name too long? No problem, we'll truncate it.

    new_name = new_name[0:120]

    urllist = UrlList.objects.all().filter(account=account, id=list_id, is_deleted=False).first()
    if not urllist:
        return False

    urllist.name = new_name
    urllist.save()

    return True


def get_urllists_from_account(account: Account) -> Dict:
    """
    These are lists with some metadata. The metadata is used to give an indication how many urls etc (#52) are
    included. Note that this does not return the entire set of urls, given that URLS may be in the thousands.
    A few times a thousand urls will load slowly, which is detrimental to the user experience.

    :param account:
    :return:
    """

    # this prefetch is pretty fast.
    last_scan_prefetch = Prefetch(
        'accountinternetnlscan_set',
        queryset=AccountInternetNLScan.objects.order_by('-id').select_related('scan'),
        to_attr='last_scan'
    )

    # Selecting the whole object is extremely slow as the reports are very large, therefore we use .only to limit
    # the number of fields returned. Then the prefetch is pretty fast again.
    last_report_prefetch = Prefetch(
        'urllistreport_set',
        # filter(pk=UrlListReport.objects.latest('id').pk).
        queryset=UrlListReport.objects.order_by('-id').only('id', 'at_when'),
        to_attr='last_report'
    )

    urllists = UrlList.objects.all().filter(
        account=account,
        is_deleted=False
    ).annotate(num_urls=Count('urls')).order_by('name').prefetch_related(last_scan_prefetch, last_report_prefetch)

    # this will create a warning if the number of domains in the list > max_domains
    # This is placed outside the loop to save a database query per time this is needed.
    max_domains = config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST

    url_lists = []
    # Not needed to check the contest of the list. If it's empty, then there is just an empty list returned.
    for urllist in urllists:

        list_warnings = []
        if urllist.num_urls > max_domains:
            list_warnings.append('WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED')

        url_lists.append({
            'id': urllist.id,
            'name': urllist.name,
            'num_urls': urllist.num_urls,
            'enable_scans': urllist.enable_scans,
            'scan_type': urllist.scan_type,
            'automated_scan_frequency': urllist.automated_scan_frequency,
            'scheduled_next_scan': urllist.scheduled_next_scan,
            'last_scan_id': None if not len(urllist.last_scan) else urllist.last_scan[0].scan.id,
            'last_scan': None if not len(urllist.last_scan) else urllist.last_scan[0].started_on.isoformat(),
            'last_scan_finished': None if not len(urllist.last_scan) else urllist.last_scan[0].finished,
            'scan_now_available': urllist.is_scan_now_available(),
            'last_report_id': None if not len(urllist.last_report) else urllist.last_report[0].id,
            'last_report_date': None if not len(urllist.last_report) else urllist.last_report[0].at_when,
            'list_warnings': list_warnings
        })

    # Sprinkling an activity stream action.
    action.send(account, verb='retrieved domain lists', public=False)

    return {'lists': url_lists, 'maximum_domains_per_list': max_domains}


def get_urllist_content(account: Account, urllist_id: int) -> dict:
    """
    This will retrieve the contents of an urllist. The amount of urls can be in the thousands, and have to be displayed
    properly.

    :param account:
    :param urllist_name:
    :return:
    """
    # This prefetch changes a 1000 ms nested query into a 150 ms query.
    prefetch = Prefetch('endpoint_set',
                        queryset=Endpoint.objects.filter(protocol__in=['dns_soa', 'dns_a_aaaa'], is_dead=False),
                        to_attr='relevant_endpoints')

    # This ordering makes sure all subdomains are near the domains with the right extension.
    urls = Url.objects.all().filter(
        urls_in_dashboard_list__account=account,
        urls_in_dashboard_list__id=urllist_id
    ).order_by('computed_domain', 'computed_suffix', 'computed_subdomain').prefetch_related(prefetch).all()

    """ It's very possible that the urrlist_id is not matching with the account. The query will just return
    nothing. Only of both matches it will return something we can work with. """
    response: Dict[str, Any] = {'urllist_id': urllist_id, 'urls': []}

    """ This is just a simple iteration, all sorting and logic is placed in the vue as that is much more flexible. """
    for url in urls:
        has_mail_endpoint = len([x for x in url.relevant_endpoints if x.protocol == 'dns_soa']) > 0
        has_web_endpoint = len([x for x in url.relevant_endpoints if x.protocol == 'dns_a_aaaa']) > 0

        response['urls'].append({
            'id': url.id,
            'url': url.url,
            'subdomain': url.computed_subdomain,
            'domain': url.computed_domain,
            'suffix': url.computed_suffix,
            'created_on': url.created_on,
            'resolves': not url.not_resolvable,
            'has_mail_endpoint': has_mail_endpoint,
            'has_web_endpoint': has_web_endpoint
        })

    return response


def retrieve_urls_from_unfiltered_input(garbage: str) -> List[str]:
    # Protocols are irrelevant:
    garbage = garbage.replace("http://", "")
    garbage = garbage.replace("https://", "")

    # Allow CSV, newlines, tabs and space-split input
    garbage = garbage.replace(",", " ")
    garbage = garbage.replace("\n", " ")
    garbage = garbage.replace("\t", " ")

    # Split also removes double spaces etc
    garbage = garbage.split(" ")

    # now remove _all_ whitespace characters
    garbage = [re.sub(r"\s+", " ", u) for u in garbage]

    # remove port numbers and paths
    garbage = [re.sub(r":[^\s]*", "", u) for u in garbage]

    # remove paths, directories etc
    garbage = [re.sub(r"/[^\s]*", "", u) for u in garbage]

    # make list unique
    garbage = list(set(garbage))

    # Remove empty values
    while "" in garbage:
        garbage.remove("")

    # make sure the list is in alphabetical order, which is nice for testability.
    return sorted(garbage)


def save_urllist_content(account: Account, user_input: Dict[str, Any]) -> Dict:
    """
    This is the 'id' version of save_urllist. It is a bit stricter as in that it requires the list to exist.

    Stores urls in an urllist. If the url doesn't exist yet, it will be added to the database (so the urls
    can be shared with multiple accounts, and only requires one scan).

    Used in the web / ajax frontend and uses operation responses.

    :param account:
    :param user_input:
    :return:
    """

    # how could we validate user_input a better way? Using a validator object?
    list_id = user_input.get('list_id')
    urls = user_input.get('urls')

    urllist = UrlList.objects.all().filter(account=account, id=list_id, is_deleted=False, ).first()

    if not urllist:
        return operation_response(error=True, message="List does not exist")

    urls = retrieve_urls_from_unfiltered_input(urls)
    cleaned_urls = clean_urls(urls)  # type: ignore

    if cleaned_urls['correct']:
        counters = _add_to_urls_to_urllist(account, urllist, urls=cleaned_urls['correct'])
    else:
        counters = {'added_to_list': 0, 'already_in_list': 0}

    result = {'incorrect_urls': cleaned_urls['incorrect'],
              'added_to_list': counters['added_to_list'],
              'already_in_list': counters['already_in_list']}

    return operation_response(success=True, message="Valid urls have been added", data=result)


def save_urllist_content_by_name(account: Account, urllist_name: str, urls: List[str]) -> dict:
    """
    This 'by name' variant is a best guess when a spreadsheet upload with list names is used.

    Stores urls in an urllist. If the url doesn't exist yet, it will be added to the database (so the urls
    can be shared with multiple accounts, and only requires one scan).

    Lists that don't exist will be created on the fly. The hope is to prevent data loss.

    Do not attempt to create a list if there are no valid urls for it, that would be a waste.

    Urls are just strings, which is enough to determine if it should be added.
    """

    cleaned_urls = clean_urls(urls)

    if cleaned_urls['correct']:
        urllist = get_or_create_list_by_name(account=account, name=urllist_name)
        counters = _add_to_urls_to_urllist(account, urllist, urls=cleaned_urls['correct'])
    else:
        counters = {'added_to_list': 0, 'already_in_list': 0}

    result = {'incorrect_urls': cleaned_urls['incorrect'],
              'added_to_list': counters['added_to_list'],
              'already_in_list': counters['already_in_list']}

    return result


def _add_to_urls_to_urllist(account: Account, current_list: UrlList, urls: List[str]) -> Dict[str, Any]:

    counters: Dict[str, int] = {'added_to_list': 0, 'already_in_list': 0}

    for url in urls:

        # if already in list, don't need to save it again
        already_in_list = UrlList.objects.all().filter(
            account=account, id=current_list.id, urls__url__iexact=url).exists()
        if already_in_list:
            counters['already_in_list'] += 1
            continue

        # if url already in database, we only need to add it to the list:
        existing_url = Url.objects.all().filter(url=url).first()
        if existing_url:
            current_list.urls.add(existing_url)
            counters['added_to_list'] += 1
        else:
            new_url = Url.add(url)

            # always try to find a few dns endpoints...
            compose_discover_task(urls_filter={'pk': new_url.id}).apply_async()

            current_list.urls.add(new_url)
            counters['added_to_list'] += 1

    return counters


def clean_urls(urls: List[str]) -> Dict[str, List]:
    """
    Incorrect urls are urls that are not following the uri scheme standard and don't have a recognizable suffix. They
    are returned for informational purposes and can contain utter garbage. The editor of the urls can then easily see
    if the urls are entered correctly and might correct some mistakes.

    :param urls:
    :return:
    """

    result: Dict[str, List] = {'incorrect': [], 'correct': []}

    for url in urls:
        # all urls in the system must be lowercase (if applicable to used character)
        url = url.lower()

        if not Url.is_valid_url(url):
            result['incorrect'].append(url)
        else:
            result['correct'].append(url)

    return result


def get_or_create_list_by_name(account, name: str) -> UrlList:

    existing_list = UrlList.objects.all().filter(account=account, name=name, is_deleted=False,).first()

    if existing_list:
        return existing_list
    else:
        urllist = UrlList(**{'name': name, 'account': account})
        urllist.save()
        return urllist


def delete_url_from_urllist(account: Account, urllist_id: int, url_id: int) -> Tuple[int, Dict[str, int]]:
    """
    While we delete the url in the urllist, the actual url is not deleted. It might be used by others, and
    all the same it might be used in the future by someone else. This will retrain the historic data.

    :param account:
    :param urllist_id:
    :param url_id:
    :return:
    """

    return Url.objects.all().filter(
        urls_in_dashboard_list__account=account,
        urls_in_dashboard_list__id=urllist_id,
        id=url_id).delete()
