"""
These testcases help to validate the working of the listmanagement API.

Run these tests with tox -e test
"""


import logging

from dashboard.internet_nl_dashboard.listmanagement import (create_list, delete_list,
                                                            delete_url_from_urllist,
                                                            get_urllist_content,
                                                            save_urllist_content)
from dashboard.internet_nl_dashboard.models import Account

logging.disable(logging.NOTSET)
log = logging.getLogger(__package__)


def test_urllists(db) -> None:
    account, created = Account.objects.all().get_or_create(name="test")

    list_1 = create_list(account, "test list 1")
    list_1_remake = create_list(account, "test list 1")
    assert list_1 == list_1_remake

    list_2 = create_list(account, "test list 2")
    assert list_1 != list_2

    list_content = get_urllist_content(account=account, urllist_name="test list 1")
    assert len(list_content['urls']) == 0

    """ Should be no problem to add the same urls, it just has not so much effect. """
    added = save_urllist_content(account, "test list 1", ['test.nl', 'internet.nl', 'internetcleanup.foundation'])
    assert added['added_to_list'] == 3 and added['already_in_list'] == 0 and len(added['incorrect_urls']) == 0

    already = save_urllist_content(account, "test list 1", ['test.nl', 'internet.nl', 'internetcleanup.foundation'])
    assert already['added_to_list'] == 0 and already['already_in_list'] == 3 and len(already['incorrect_urls']) == 0

    list_content = get_urllist_content(account=account, urllist_name="test list 1")
    assert len(list_content['urls']) == 3

    """ Garbage urls should be filtered out and can be displayed as erroneous """
    already = save_urllist_content(account, "test list 1", ['test.nonse^', 'NONSENSE', '127.0.0.1'])
    assert already['added_to_list'] == 0 and already['already_in_list'] == 0 and len(already['incorrect_urls']) == 3

    """ Check if really nothing was added """
    list_content = get_urllist_content(account=account, urllist_name="test list 1")
    assert len(list_content['urls']) == 3

    """ Delete a a urls from the list: """
    items_deleted, item_details = delete_url_from_urllist(account, "test list 1", 'test.nl')
    # {'internet_nl_dashboard.UrlList_urls': 1, 'organizations.Url': 1,
    # 'organizations.Url_organization': 0, 'pro.RescanRequest': 0, ...}
    """ The testcase delivers 2 deleted items, including an organizations.Url, this is weird, since we're not doing
    anything with the organization. """
    assert items_deleted == 2
    list_content = get_urllist_content(account=account, urllist_name="test list 1")
    assert len(list_content['urls']) == 2

    """ Delete the entire list, we'll get nothing back, only an empty response. """
    items_deleted, item_details = delete_list(account, urllist_name="test list 1")

    # it deletes two urls and the list itself, makes 3
    assert items_deleted == 3
    list_content = get_urllist_content(account=account, urllist_name="test list 1")
    assert len(list_content['urls']) == 0

    account2, created = Account.objects.all().get_or_create(name="test 2")
    """ You cannot delete things from another account """
    items_deleted, item_details = delete_list(account2, urllist_name="test list 1")
    assert items_deleted == 0
