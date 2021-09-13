from typing import List

from dashboard.internet_nl_dashboard.logic.domains import (_add_to_urls_to_urllist,
                                                           get_or_create_list_by_name)
from dashboard.internet_nl_dashboard.logic.tags import add_tag, remove_tag, tags_in_urllist
from dashboard.internet_nl_dashboard.models import TaggedUrlInUrllist
from tests import make_url_with_endpoint_and_scan


def validate(url_id, urllist_id, expected_tags: List[str]):
    first_taglist = TaggedUrlInUrllist.objects.all().filter(url=url_id, urllist=urllist_id).first()

    if not first_taglist:
        raise SystemError

    assert list(first_taglist.tags.names()) == expected_tags


def test_tags(db):  # pylint: disable=invalid-name, unused-argument
    account, url, _, _ = make_url_with_endpoint_and_scan()
    my_list = get_or_create_list_by_name(account, name="test list 1", scan_type="mail")
    _add_to_urls_to_urllist(account, my_list, [url])

    validate(url.id, my_list.id, [])
    add_tag(account, [url.id], my_list.id, "test_tag")
    validate(url.id, my_list.id, ['test_tag'])
    add_tag(account, [url.id], my_list.id, "test_tag_2")
    add_tag(account, [url.id], my_list.id, "test_tag_3")
    assert tags_in_urllist(account, my_list.id) == ['test_tag', 'test_tag_2', 'test_tag_3']
    remove_tag(account, [url.id], my_list.id, "test_tag")
    remove_tag(account, [url.id], my_list.id, "test_tag_2")
    remove_tag(account, [url.id], my_list.id, "test_tag_3")
    validate(url.id, my_list.id, [])
