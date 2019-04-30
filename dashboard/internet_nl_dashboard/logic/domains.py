import logging
from typing import Any, Dict, List, Tuple

from django.db.models import Prefetch
from django.utils import timezone
from tldextract import tldextract
from validators import domain
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint
from websecmap.scanners.scanner.dns_endpoints import compose_discover_task

from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList

# import pysnooper


log = logging.getLogger(__package__)


def operation_response(error: bool = False, success: bool = False, message: str = "", data: Dict = None):
    return {'error': error, 'success': success, 'message': message, 'state': "error" if error else "success",
            'data': data}


# todo: write test
def alter_url_in_urllist(account, data):
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
    if not is_valid_url(data['new_url_string']):
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

    return operation_response(success=True, message="Saved.", data={
        'created': {'id': new_url.id, 'url': new_url.url, 'created_on': new_url.created_on,
                    'has_mail_endpoint': new_url_has_mail_endpoint,
                    'has_web_endpoint': new_url_has_web_endpoint},
        'removed': {'id': old_url.id, 'url': old_url.url, 'created_on': old_url.created_on,
                    'has_mail_endpoint': old_url_has_mail_endpoint,
                    'has_web_endpoint': old_url_has_web_endpoint},
    })


def is_valid_url(url):
    extract = tldextract.extract(url)
    if not extract.suffix:
        return False

    # Validators catches 'most' invalid urls, but there are some issues and exceptions that are not really likely
    # to cause any major issues in our software. The other alternative is another library with other quircks.
    # see: https://github.com/kvesteri/validators/
    # Note that this library does not account for 'idna' / punycode encoded domains, so you have to convert
    # them yourself. luckily:
    # 'аренда.орг' -> 'xn--80aald4bq.xn--c1avg'
    # 'google.com' -> 'google.com'
    valid_domain = domain(url.encode('idna').decode())
    if valid_domain is not True:
        return False

    return True


def get_url(new_url_string: str):

    # first check if one exists, if not, create it.
    url = Url.objects.all().filter(url=new_url_string).first()
    if url:
        return url, False

    # url does not exist, create it.
    if not is_valid_url(new_url_string):
        raise ValueError('Invalid Url')

    new_url = Url()
    new_url.url = new_url_string
    new_url.created_on = timezone.now()
    new_url.save()

    # start finding endpoints after url has been created.
    trigger_async_endpoint_scan(new_url)

    return new_url, True


def trigger_async_endpoint_scan(url: Url):
    compose_discover_task(urls_filter={'pk': url.id}).apply_async()


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
        'scheduled_next_scan': UrlList.determine_next_scan_moment(frequency)
    }

    urllist = UrlList(**data)
    urllist.save()

    # make sure the account is serializable.
    data['account'] = account.id

    # adding the ID makes it possible to add new urls to a new list.
    data['id'] = urllist.pk

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
    urllist.deleted_on = timezone.now()
    urllist.save()

    return operation_response(success=True, message="List deleted.")


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

    prefetch = Prefetch(
        'accountinternetnlscan_set',
        queryset=AccountInternetNLScan.objects.order_by('-id').select_related('scan'),
        to_attr='last_scan'
    )

    urllist = UrlList.objects.all().filter(
        account=account,
        id=user_input['id'],
        is_deleted=False
    ).prefetch_related(prefetch).first()

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

    updarted_urllist = UrlList(**data)
    updarted_urllist.save()

    # make sure the account is serializable.
    data['account'] = account.id

    # inject the last scan information.
    data['last_scan'] = None if not len(urllist.last_scan) else urllist.last_scan[0].scan.started_on.isoformat()
    data['last_scan_finished'] = None if not len(urllist.last_scan) else urllist.last_scan[0].scan.finished

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


def get_urllists_from_account(account: Account) -> List:
    """
    These are lists with some metadata. The metadata is used to give an indication how many urls etc (todo) are
    included. Note that this does not return the entire set of urls, given that URLS may be in the thousands.
    A few times a thousand urls will load slowly, which is detrimental to the user experience.

    :param account:
    :return:
    """

    prefetch = Prefetch(
        'accountinternetnlscan_set',
        queryset=AccountInternetNLScan.objects.order_by('-id').select_related('scan'),
        to_attr='last_scan'
    )

    urllists = UrlList.objects.all().filter(
        account=account,
        is_deleted=False
    ).order_by('name').prefetch_related(prefetch).all()

    response = []
    # todo: amount of urls, dead_urls etc... Probably add lifecycle to this?
    # Not needed to check the contest of the list. If it's empty, then there is just an empty list returned.
    for urllist in urllists:
        response.append({
            'id': urllist.id,
            'name': urllist.name,
            'enable_scans': urllist.enable_scans,
            'scan_type': urllist.scan_type,
            'automated_scan_frequency': urllist.automated_scan_frequency,
            'scheduled_next_scan': urllist.scheduled_next_scan,
            'last_scan': None if not len(urllist.last_scan) else urllist.last_scan[0].scan.started_on.isoformat(),
            'last_scan_finished': None if not len(urllist.last_scan) else urllist.last_scan[0].scan.finished
        })

    return response


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

    urls = Url.objects.all().filter(
        urls_in_dashboard_list__account=account,
        urls_in_dashboard_list__id=urllist_id
    ).order_by('url').prefetch_related(prefetch).all()

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
            'created_on': url.created_on,
            'resolves': not url.not_resolvable,
            'has_mail_endpoint': has_mail_endpoint,
            'has_web_endpoint': has_web_endpoint
        })

    return response


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

    # todo: how to work with data types in dicts like this?
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
            # todo: might be wise to use bulk_create to speed up insertion
            new_url = Url(**{'url': url})
            new_url.save()
            trigger_async_endpoint_scan(new_url)
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

        if not is_valid_url(url):
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


def delete_url_from_urllist(account: Account, urllist_name: str, url: str) -> Tuple[int, Dict[str, int]]:
    """
    While we delete the url in the urllist, the actual url is not deleted. It might be used by others, and
    all the same it might be used in the future by someone else. This will retrain the historic data.

    :param account:
    :param urllist_name:
    :param url:
    :return:
    """

    return Url.objects.all().filter(
        urls_in_dashboard_list__account=account,
        urls_in_dashboard_list__name=urllist_name,
        url=url).delete()
