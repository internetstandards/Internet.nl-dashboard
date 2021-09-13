from typing import List

from taggit.models import Tag

from dashboard.internet_nl_dashboard.models import Account, TaggedUrlInUrllist


def add_tag(account: Account, url_ids: List[int], urllist_id: int, tag: str) -> None:
    taggables = TaggedUrlInUrllist.objects.all().filter(url__in=url_ids, urllist=urllist_id, urllist__account=account)
    for taggable in taggables:
        taggable.tags.add(tag[0:40])


def remove_tag(account: Account, url_ids: List[int], urllist_id: int, tag: str) -> None:
    taggables = TaggedUrlInUrllist.objects.all().filter(url__in=url_ids, urllist=urllist_id, urllist__account=account)
    for taggable in taggables:
        taggable.tags.remove(tag)


def tags_in_urllist(account: Account, urllist_id: int) -> List[str]:

    return list(Tag.objects.all().filter(
        taggedurlinurllist__urllist=urllist_id,
        taggedurlinurllist__urllist__account=account
    ).values_list('name', flat=True))
