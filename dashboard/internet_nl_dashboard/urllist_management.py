from typing import List

from tldextract import tldextract
from websecmap.organizations.models import Url

from dashboard.internet_nl_dashboard.models import Account, UrlList


def get_urllists_from_account(account: Account):
    """
    These are lists with some metadata. The metadata is used to give an indication how many urls etc (todo) are
    included. Note that this does not return the entire set of urls, given that URLS may be in the thousands.
    A few times a thousand urls will load slowly, which is detrimental to the user experience.

    :param account:
    :return:
    """
    urllists = UrlList.objects.all().filter(account=account)

    response = []
    # todo: amount of urls, dead_urls etc... Probably add lifecycle to this?
    # Not needed to check the contest of the list. If it's empty, then there is just an empty list returned.
    for urllist in urllists:
        response.append({
            'id': urllist.id,
            'name': urllist.name
        })

    return response


def get_urllist_content(account: Account, urllist_name: str):
    """
    This will retrieve the contents of an urllist. The amount of urls can be in the thousands, and have to be displayed
    properly.

    :param account:
    :param urllist_name:
    :return:
    """
    urls = Url.objects.all().filter(urls_in_dashboard_list__account=account, urls_in_dashboard_list__name=urllist_name)

    """ It's very possible that the urrlist_id is not matching with the account. The query will just return
    nothing. Only of both matches it will return something we can work with. """
    response = {'urllist_name': urllist_name, 'urls': []}

    """ This is just a simple iteration, all sorting and logic is placed in the vue as that is much more flexible. """
    for url in urls:
        response['urls'].append({
            'url': url.url,
            'created_on': url.created_on,
            'resolves': not url.not_resolvable,
            'is_dead': url.is_dead
        })

    return response


def save_urllist_content(account: Account, urllist_name: str, urls: List[str]):
    """ Stores urls in an urllist. If the url doesn't exist yet, it will be added to the database (so the urls
    can be shared with multiple accounts, and only requires one scan).

    Lists that don't exist will be created on the fly. The hope is to prevent data loss.

    Do not attempt to create a list if there are no valid urls for it, that would be a waste.

    Urls are just strings, which is enough to determine if it should be added.
    """

    cleaned_urls = clean_urls(urls)

    if cleaned_urls['correct']:
        urllist = create_list(account=account, name=urllist_name)
        counters = _add_to_urls_to_urllist(account, urllist.name, urls=cleaned_urls['correct'])
    else:
        counters = {'added_to_list': 0, 'already_in_list': 0, 'incorrect_urls': cleaned_urls['incorrect']}

    result = {'incorrect_urls': cleaned_urls['incorrect'],
              'added_to_list': counters['added_to_list'],
              'already_in_list': counters['already_in_list']}

    return result


def _add_to_urls_to_urllist(account: Account, urllist_name: str, urls: List[str]):

    counters = {'added_to_list': 0, 'already_in_list': 0, 'error': 0, 'message': ''}

    current_list = UrlList.objects.all().filter(name=urllist_name).first()
    if not current_list:
        current_list = create_list(account, urllist_name)

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


def clean_urls(urls: List[str]):
    """
    Incorrect urls are urls that are not following the uri scheme standard and don't have a recognizable suffix. They
    are returned for informational purposes and can contain utter garbage. The editor of the urls can then easily see
    if the urls are entered correctly and might correct some mistakes.

    :param urls:
    :return:
    """

    result = {'incorrect': [], 'correct': []}

    for url in urls:
        url = url.lower()
        extract = tldextract.extract(url)

        if not extract.suffix:
            result['incorrect'].append(url)
            continue

        result['correct'].append(url)

    return result


def create_list(account, name: str) -> UrlList:

    existing_list = UrlList.objects.all().filter(account=account, name=name).first()

    if existing_list:
        return existing_list
    else:
        urllist = UrlList(**{'name': name, 'account': account})
        urllist.save()
        return urllist


def delete_url_from_urllist(account: Account, urllist_name: str, url: str):
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


def delete_list(account: Account, urllist_name: str):
    """
    A list can really be deleted and isn't a 'precious' resource. It can quickly be re-created with imports from
    excel or just a copy paste of a series of strings.

    :param account:
    :param urllist_name:
    :return:
    """

    return UrlList.objects.all().filter(account=account, name=urllist_name).delete()
