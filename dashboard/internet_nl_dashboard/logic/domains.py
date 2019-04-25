import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import pytz
from django.db.models import Prefetch
from django.utils import timezone
from tldextract import tldextract
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint

from dashboard.internet_nl_dashboard.models import Account, UrlList

# import pysnooper


log = logging.getLogger(__package__)


def operation_response(error: bool = False, success: bool = False, message: str = "", data: Dict = None):
    return {'error': error, 'success': success, 'message': message, 'state': "error" if error else "success",
            'data': data}


def determine_next_scan_moment(preference: str):
    """
    Converts one of the (many) string options to the next sensible date/time combination in the future.

    disabled: yesterday.
    every half year: first upcoming 1 july or 1 january
    at the start of every quarter: 1 january, 1 april, 1 juli, 1 october
    every 1st day of the month: 1 january, 1 february, etc.
    twice per month: 1 january, 1 january + 2 weeks, 1 february, 1 february + 2 weeks, etc

    :param preference:
    :return:
    """
    now = timezone.now()

    if preference == 'disabled':
        return now - timedelta(days=1)

    # months are base 1: january = 1 etc.
    if preference == 'every half year':
        if now.month in range(1, 6):
            return datetime(year=now.year, month=7, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
        return datetime(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)

    if preference == 'at the start of every quarter':
        if now.month in range(1, 3):
            return datetime(year=now.year, month=4, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
        if now.month in range(4, 6):
            return datetime(year=now.year, month=4, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
        if now.month in range(7, 9):
            return datetime(year=now.year, month=4, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
        if now.month in range(10, 12):
            return datetime(year=now.year+1, month=1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)

    if preference == 'every 1st day of the month':
        if now.month == 12:
            return datetime(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
        return datetime(year=now.year, month=now.month + 1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)

    if preference == 'twice per month':
        # since the 14'th day never causes a month or year rollover, we can simply schedule for the 15th day.
        if now.day in range(1, 14):
            return datetime(year=now.year, month=now.month, day=15, hour=0, minute=0, second=0, tzinfo=pytz.utc)

        # otherwise exactly the same as the 1st day of every month
        if now.month == 12:
            return datetime(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
        return datetime(year=now.year, month=now.month + 1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)


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
        'scheduled_next_scan': determine_next_scan_moment(frequency)
    }

    urllist = UrlList(**data)
    urllist.save()

    # make sure the account is serializable.
    data['account'] = account.id

    return operation_response(success=True, message="List created.", data=data)


def delete_list(account: Account, list_id: int):
    """
    The first assumption was that a list is not precious or special, and that it can be quickly re-created with an
    import from excel or a csv paste in the web interface. Yet this assumption is wrong. It's valuable to keep the list
    also after it is deleted. This gives insight into what scans have happened in the past on what list.

    To do that, the is_deleted columns have been introduced.

    :param account:
    :param list_id:
    :return:
    """
    urllist = UrlList.objects.all().filter(account=account, id=list_id, is_deleted=False).first()
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
    if sorted(user_input.keys()) != sorted(expected_keys):
        return operation_response(error=True, message="Missing settings.")

    urllist = UrlList.objects.all().filter(account=account, id=user_input['id'], is_deleted=False).first()

    if not urllist:
        return operation_response(error=True, message="No list of urls found.")

    # Yes, you can try and set any value. Values that are not recognized do not result in errors / error messages,
    # instead they will be overwritten with the default. This means less interaction with users / less annoyance over
    # errors on such simple forms.
    urllist.name = validate_list_name(user_input['name'])
    urllist.enable_scans = bool(user_input['enable_scans'])
    urllist.scan_type = validate_list_scan_type(user_input['scan_type'])
    urllist.automated_scan_frequency = validate_list_automated_scan_frequency(user_input['automated_scan_frequency'])
    urllist.save()

    return operation_response(success=True, message="Updated list settings")


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
    urllists = UrlList.objects.all().filter(account=account, is_deleted=False).order_by('name')

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
            'url': url.url,
            'created_on': url.created_on,
            'resolves': not url.not_resolvable,
            'has_mail_endpoint': has_mail_endpoint,
            'has_web_endpoint': has_web_endpoint
        })

    return response


def save_urllist_content(account: Account, urllist_name: str, urls: List[str]) -> dict:
    """ Stores urls in an urllist. If the url doesn't exist yet, it will be added to the database (so the urls
    can be shared with multiple accounts, and only requires one scan).

    Lists that don't exist will be created on the fly. The hope is to prevent data loss.

    Do not attempt to create a list if there are no valid urls for it, that would be a waste.

    Urls are just strings, which is enough to determine if it should be added.
    """

    cleaned_urls = clean_urls(urls)

    if cleaned_urls['correct']:
        urllist = create_list_by_name(account=account, name=urllist_name)
        counters = _add_to_urls_to_urllist(account, urllist.name, urls=cleaned_urls['correct'])
    else:
        counters = {'added_to_list': 0, 'already_in_list': 0}

    result = {'incorrect_urls': cleaned_urls['incorrect'],
              'added_to_list': counters['added_to_list'],
              'already_in_list': counters['already_in_list']}

    return result


def _add_to_urls_to_urllist(account: Account, urllist_name: str, urls: List[str]) -> Dict[str, Any]:

    counters: Dict[str, int] = {'added_to_list': 0, 'already_in_list': 0}

    current_list = UrlList.objects.all().filter(name=urllist_name, is_deleted=False).first()
    if not current_list:
        current_list = create_list_by_name(account, urllist_name)

    for url in urls:

        # if already in list, don't need to save it again
        already_in_list = UrlList.objects.all().filter(
            account=account, name=urllist_name, urls__url__iexact=url).exists()
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
        url = url.lower()
        extract = tldextract.extract(url)

        if not extract.suffix:
            result['incorrect'].append(url)
            continue

        result['correct'].append(url)

    return result


def create_list_by_name(account, name: str) -> UrlList:

    existing_list = UrlList.objects.all().filter(account=account, name=name, is_deleted=False).first()

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
