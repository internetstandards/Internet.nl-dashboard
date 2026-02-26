from typing import List

from taggit.models import Tag

from dashboard.internet_nl_dashboard.models import TAG_MAX_LENGTH, Account, TaggedUrlInUrllist


def parse_tags_from_csv_data(csv_data: str) -> List[str]:
    try:
        # When floats or other data types are present in spreadsheet uploads / user input.
        return normalize_tags(csv_data.split(","))
    except AttributeError:
        return []


def normalize_tags(tags: list[str]) -> list[str]:
    # This is not a oneliner as there might be more cleaning steps in the future.
    # tags returned are unique, lowercase, stripped and non-empty
    cleaned_tags = []
    cleaned_tags.extend(normalize_tag(tag) for tag in tags)
    cleaned_tags = list(sorted(set(cleaned_tags)))
    if "" in cleaned_tags:
        cleaned_tags.remove("")
    return cleaned_tags


def normalize_tag(tag: str):
    # None, etc
    if not tag:
        return ""

    tag = tag.lower().strip()
    return tag[:TAG_MAX_LENGTH]


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

    return list(
        sorted(
            Tag.objects.all()
            .filter(
                taggedurlinurllist__urllist=urllist_id,
                taggedurlinurllist__urllist__account=account,
            )
            .values_list("name", flat=True)
            .distinct()
        )
    )
