"""
These testcases help to validate the working of the listmanagement API.

Run these tests with tox -e test -- -k test_urllist_management
"""
from websecmap.organizations.models import Url

from dashboard.internet_nl_dashboard.logic.domains import (
    delete_list, delete_url_from_urllist, get_or_create_list_by_name, get_urllist_content,
    get_urllists_from_account, keys_are_present_in_object, rename_list,
    retrieve_possible_urls_from_unfiltered_input, save_urllist_content_by_name)
from dashboard.internet_nl_dashboard.models import Account


def test_keys_match():
    # a, b, c in any object
    assert keys_are_present_in_object(expected_keys=['a', 'b', 'c'], any_object={
                                      'a': 1, 'b': 2, 'c': 3, 'd': 4}) is True

    # Missing b
    assert keys_are_present_in_object(expected_keys=['a', 'b', 'c'], any_object={'a': 1, 'c': 3, 'd': 4}) is False

    # No expectation should always match
    assert keys_are_present_in_object(expected_keys=[], any_object={'a': 1, 'b': 2, 'c': 3, 'd': 4}) is True


def test_retrieve_urls_from_unfiltered_input() -> None:
    output, duplicates_removed = retrieve_possible_urls_from_unfiltered_input(
        "https://www.apple.com:443/nl/iphone-11/, bing.com, http://nu.nl, nu.nl")
    assert output == ['bing.com', 'nu.nl', 'www.apple.com']
    # one nu.nl removed
    assert duplicates_removed == 1

    # input contains multiple lines, whitespaces before and after the domains and some tabs mixed in.

    # \s in regex only filters out: \t\n\r\f\v not all whitespace characters in unicode.
    # All examples for https://qwerty.dev/whitespace/ are in the below input, which is invisible to the naked eye :)
    unsanitized_input = """
    ,  
     stichtingmediawijzer.nl	  ​ 
            , , ,   ⠀ 
     	   
    eskillsplatform.nl  ,        
    """  # noqa violates python coding standard on points E101 and W191. Needed for this test :)

    output, duplicates_removed = retrieve_possible_urls_from_unfiltered_input(unsanitized_input)
    # Zero width space is also seen as a string, and filtered out as a possible domain. See test_clean_urls.
    assert output == [' ', ' ⠀ ', 'eskillsplatform.nl', 'stichtingmediawijzer.nl', '\u200b ']


def test_urllists(db, redis_server) -> None:
    account, created = Account.objects.all().get_or_create(name="test")

    list_1 = get_or_create_list_by_name(account, "test list 1")
    list_1_remake = get_or_create_list_by_name(account, "test list 1")
    assert list_1 == list_1_remake

    list_2 = get_or_create_list_by_name(account, "test list 2")
    assert list_1 != list_2

    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 0

    """ We made two lists, so we expect to see two lists returned """
    lists = get_urllists_from_account(account=account)
    assert len(lists) == 2

    """ Should be no problem to add the same urls, it just has not so much effect. """
    added = save_urllist_content_by_name(
        account, "test list 1", ['test.nl', 'internet.nl', 'internetcleanup.foundation'])
    assert added['added_to_list'] == 3 and added['already_in_list'] == 0 and len(added['incorrect_urls']) == 0

    already = save_urllist_content_by_name(
        account, "test list 1", ['test.nl', 'internet.nl', 'internetcleanup.foundation'])
    assert already['added_to_list'] == 0 and already['already_in_list'] == 3 and len(already['incorrect_urls']) == 0

    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 3

    """ Garbage urls should be filtered out and can be displayed as erroneous """
    already = save_urllist_content_by_name(account, "test list 1", ['test.nonse^', 'NONSENSE', '127.0.0.1'])
    assert already['added_to_list'] == 0 and already['already_in_list'] == 0 and len(already['incorrect_urls']) == 3

    """ Check if really nothing was added """
    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 3

    # make sure the url gets deleted from the urllist and not from the database
    urls_in_database = Url.objects.all().count()
    assert urls_in_database == 3

    """ Delete a a urls from the list: """
    url_got_removed_from_list = delete_url_from_urllist(account, list_1.id,
                                                        Url.objects.all().filter(url='test.nl').first().id)

    assert urls_in_database == Url.objects.all().count()

    assert url_got_removed_from_list is True
    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 2

    """ Delete the entire list, we'll get nothing back, only an empty response. """
    operation_response = delete_list(account=account, user_input={'id': list_1.id})

    # it deletes two urls and the list itself, makes 3
    assert operation_response['success'] is True
    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)

    # deletion is administrative, so the urls are still connected.
    assert len(list_content['urls']) == 2

    account2, created = Account.objects.all().get_or_create(name="test 2")
    """ You cannot delete things from another account """
    operation_response = delete_list(account=account2, user_input={'id': list_1.id})
    assert operation_response['success'] is False

    """ A new list will not be created if there are no urls for it..."""
    added = save_urllist_content_by_name(account, "should be empty", [])
    assert added['added_to_list'] == 0 and added['already_in_list'] == 0 and len(added['incorrect_urls']) == 0

    """ A new list will not be created if there are only nonsensical urls (non valid) for it """
    added = save_urllist_content_by_name(account, "should be empty", ['iuygvb.uighblkj'])

    list_content = get_urllist_content(account=account, urllist_id=9001)
    assert len(list_content['urls']) == 0

    # list can be renamed
    renamed = rename_list(account=account, list_id=list_2.pk, new_name="A new name")
    assert renamed is True

    # lists can have the same name (does not work with list_1... why not?)
    renamed = rename_list(account=account, list_id=list_2.pk, new_name="A new name")
    assert renamed is True

    # lists can have an awfully long name and that will not be a problem, as it is truncated
    renamed = rename_list(account=account, list_id=list_2.pk, new_name="alksdnalksdnlaksdnlasdknasldknaldnalskndnlaksn"
                                                                       "asdnlkansdlknansldknasldnalkndwlkawdnlkdwanlkn"
                                                                       "aksjdnaksjdndaslkdnlaklwkndlkawndwlakdnwlakkln"
                                                                       "ansdknlaslkdnlaknwdlknkldawnldkwanlkadwnlkdawn"
                                                                       "awdnawklnldndawlkndwalkndaklndwaklnwalkdnwakln"
                                                                       "adlkwndlknawkdlnawldknawlkdnawklndklawnwkalnkn"
                                                                       "awdlknawlkdnawlkdnalwdnawlkdnawkldnalkwndaklwn")
    assert renamed is True


def u(url: str) -> int:
    return Url.objects.all().filter(url=url).first().id


def test_delete_url_from_urllist(db, redis_server):
    a1, created = Account.objects.all().get_or_create(name="a1")
    a2, created = Account.objects.all().get_or_create(name="a2")
    l1 = get_or_create_list_by_name(a1, "l1")
    l2 = get_or_create_list_by_name(a2, "l2")
    save_urllist_content_by_name(a1, "l1", ['test.nl', 'internet.nl', 'internetcleanup.foundation'])
    save_urllist_content_by_name(a2, "l2", ['nu.nl', 'nos.nl', 'tweakers.net'])

    assert l1 != l2
    assert a1 != a2

    assert Url.objects.all().count() == 6

    assert True is delete_url_from_urllist(a1, l1.id, u('test.nl'))
    # double delete results into nothing
    assert False is delete_url_from_urllist(a1, l1.id, u('test.nl'))
    # a2 cannot delete something from the lists of a1, even if the url exist in the list from l1
    assert False is delete_url_from_urllist(a2, l1.id, u('test.nl'))
    # no crash on non-existing id's:
    assert False is delete_url_from_urllist(a1, 990000, u('test.nl'))
    assert False is delete_url_from_urllist(a1, l1.id, 9990000)

    assert Url.objects.all().count() == 6
