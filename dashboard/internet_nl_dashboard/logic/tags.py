from typing import List

from taggit.models import Tag

from dashboard.internet_nl_dashboard.models import Account, TaggedUrlInUrllist


def normalize_tag(tag: str):
    # None, etc
    if not tag:
        return ""

    tag = tag.lower()
    tag = tag[0:40]
    return tag


def add_tag(account: Account, url_ids: List[int], urllist_id: int, tag: str) -> None:

    tag = normalize_tag(tag)

    # Do not add empty tags
    if not tag:
        return

    taggables = TaggedUrlInUrllist.objects.all().filter(url__in=url_ids, urllist=urllist_id, urllist__account=account)
    for taggable in taggables:
        taggable.tags.add(tag)


def remove_tag(account: Account, url_ids: List[int], urllist_id: int, tag: str) -> None:
    tag = normalize_tag(tag)

    taggables = TaggedUrlInUrllist.objects.all().filter(url__in=url_ids, urllist=urllist_id, urllist__account=account)
    for taggable in taggables:
        taggable.tags.remove(tag)


def tags_in_urllist(account: Account, urllist_id: int) -> List[str]:

    return list(sorted(Tag.objects.all().filter(
        taggedurlinurllist__urllist=urllist_id,
        taggedurlinurllist__urllist__account=account
    ).values_list('name', flat=True).distinct()))
