# SPDX-License-Identifier: Apache-2.0
import json

from django.contrib.auth.models import User
from websecmap.organizations.models import Url

from dashboard.internet_nl_dashboard.models import Account, DashboardUser, TaggedUrlInUrllist, UrlList


def test_add_tag_to_multiple_urls(db, client):
    user = User.objects.create(username="tag-api-user")
    account = Account.objects.create(name="tag-api-account")
    DashboardUser.objects.create(user=user, account=account)
    client.force_login(user)

    urllist = UrlList.objects.create(name="tag-api-list", account=account)
    selected_urls = [Url.objects.create(url="first.example"), Url.objects.create(url="second.example")]
    unselected_url = Url.objects.create(url="unselected.example")
    urllist.urls.add(*selected_urls, unselected_url)

    response = client.post(
        f"/api/v1/urllists/{urllist.id}/urls/tags",
        data=json.dumps({"url_ids": [url.id for url in selected_urls], "tag": "Batch Tag"}),
        content_type="application/json",
    )

    assert response.status_code == 201, "Adding a tag to multiple URL IDs should succeed."
    assert response.json()["success"] is True, "The operation response should report success."

    for url in selected_urls:
        tagged_url = TaggedUrlInUrllist.objects.get(urllist=urllist, url=url)
        assert list(tagged_url.tags.names()) == ["batch tag"], "Every selected URL should receive the normalized tag."

    unselected_tagged_url = TaggedUrlInUrllist.objects.get(urllist=urllist, url=unselected_url)
    assert list(unselected_tagged_url.tags.names()) == [], "URLs omitted from url_ids should remain unchanged."


def test_add_tag_only_changes_urls_in_the_requested_account_list(db, client):
    user = User.objects.create(username="scoped-tag-api-user")
    account = Account.objects.create(name="scoped-tag-api-account")
    DashboardUser.objects.create(user=user, account=account)
    client.force_login(user)

    urllist = UrlList.objects.create(name="requested-list", account=account)
    requested_url = Url.objects.create(url="requested.example")
    urllist.urls.add(requested_url)

    other_account = Account.objects.create(name="other-tag-api-account")
    other_list = UrlList.objects.create(name="other-list", account=other_account)
    other_url = Url.objects.create(url="other.example")
    other_list.urls.add(other_url)

    response = client.post(
        f"/api/v1/urllists/{urllist.id}/urls/tags",
        data=json.dumps({"url_ids": [requested_url.id, other_url.id], "tag": "Scoped Tag"}),
        content_type="application/json",
    )

    assert response.status_code == 201, "Valid bulk-tag requests should succeed even when unrelated IDs are ignored."
    requested_tagged_url = TaggedUrlInUrllist.objects.get(urllist=urllist, url=requested_url)
    assert list(requested_tagged_url.tags.names()) == [
        "scoped tag"
    ], "The URL belonging to the requested account list should receive the tag."
    other_tagged_url = TaggedUrlInUrllist.objects.get(urllist=other_list, url=other_url)
    assert list(other_tagged_url.tags.names()) == [], "A URL in another account's list must not be changed."
