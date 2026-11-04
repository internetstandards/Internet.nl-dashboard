# SPDX-License-Identifier: Apache-2.0
import json
from datetime import timedelta
from unittest.mock import Mock

import pytest
from constance.test import override_config
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import now
from dns.exception import Timeout
from websecmap.organizations.models import Url

from dashboard.internet_nl_dashboard.logic import domain_batches as batches
from dashboard.internet_nl_dashboard.models import Account, DashboardUser, DomainBatch, DomainBatchItem, UrlList
from dashboard.internet_nl_dashboard.problems import ApiError


@pytest.fixture
def batch_user(db, client, monkeypatch, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    account = Account.objects.create(name="Batch account")
    user = User.objects.create_user(username="batch-user")
    dashboarduser = DashboardUser.objects.create(account=account, user=user)
    client.force_login(user)
    monkeypatch.setattr(batches.process_domain_batch, "send", Mock())
    monkeypatch.setattr(batches, "has_a_or_aaaa", lambda domain: True)
    monkeypatch.setattr(batches, "has_soa", lambda domain: False)
    return dashboarduser


def run_batch(data):
    batches.process_domain_batch(data["id"])
    return DomainBatch.objects.get(id=data["id"])


@override_config(DASHBOARD_MAXIMUM_DOMAINS_PER_LIST=2, DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET=25000)
def test_validation_reports_invalid_existing_and_duplicates_before_any_addition(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="Ordered")
    urllist.urls.add(Url.add("ajax.nl"))
    batch = run_batch(
        batches.start_batch(
            batch_user, urllist_id=urllist.id, raw_urls="ajax.nl\nWWW.EXAMPLE.NL\nnot-a-domain\nwww.example.nl\nlast.nl"
        )
    )
    summary = batches.batch_summary(batch)
    assert batch.status == "review", "Validation must wait for user confirmation before writing list contents."
    assert summary["counts"] == {"existing": 1, "valid": 2, "invalid": 1, "duplicate": 1}, (
        "Each supplied entry must have a visible outcome, including malformed input."
    )
    assert summary["processed"] == summary["total"] == 5, "Validation progress must count actual inspected entries."
    assert summary["limits"][0]["over_limit"] == 1, "Only new unique domains should consume the one free list place."
    assert tuple(urllist.urls.values_list("url", flat=True)) == ("ajax.nl",), (
        "Preview must leave the existing list intact."
    )
    assert batch.items.get(status="invalid").raw_domain == "not-a-domain", "Malformed input must remain editable."


@override_config(DASHBOARD_MAXIMUM_DOMAINS_PER_LIST=2)
def test_addition_respects_order_capacity_and_real_completion(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Order")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="z.nl\ndead.nl\na.nl\nb.nl"))
    snapshots = []

    def resolve(domain):
        return (False, "No DNS records") if domain == "dead.nl" else (True, "")

    original_add = Url.add

    def observed_add(domain):
        snapshots.append(batches.batch_summary(DomainBatch.objects.get(id=batch.id)))
        return original_add(domain)

    monkeypatch.setattr(Url, "add", observed_add)
    monkeypatch.setattr(batches, "resolve_domain", resolve)
    batches.confirm_batch(batch_user.account, batch.id)
    batch = run_batch({"id": batch.id})
    assert batch.status == "completed", "Completion is recorded only after all additions and rejections are persisted."
    assert set(urllist.urls.values_list("url", flat=True)) == {"z.nl", "a.nl"}, (
        "The first two resolvable domains in supplied order must fill the list, regardless of alphabetic order."
    )
    assert batch.items.get(domain="dead.nl").status == "unresolvable", "DNS rejection must not consume list capacity."
    assert batch.items.get(domain="b.nl").status == "limit", "Overflow must be reported for each skipped domain."
    assert all(snapshot["status"] == "running" for snapshot in snapshots), (
        "DNS work must never observe premature completion."
    )
    assert batches.batch_summary(batch)["percentage"] == 100, (
        "Persisted terminal outcomes must produce 100% completion."
    )


@override_config(DASHBOARD_MAXIMUM_DOMAINS_PER_LIST=1)
def test_capacity_is_rechecked_after_preview_and_duplicates_do_not_consume_it(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="Capacity")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="first.nl\nsecond.nl"))
    urllist.urls.add(Url.add("first.nl"))
    batches.confirm_batch(batch_user.account, batch.id)
    batch = run_batch({"id": batch.id})
    assert batch.items.get(domain="first.nl").status == "existing_done", (
        "A concurrent addition must be recognized as existing."
    )
    assert batch.items.get(domain="second.nl").status == "limit", (
        "Capacity must be checked again when a domain is written."
    )
    assert urllist.urls.count() == 1, "Concurrent changes must not allow the list to exceed its limit."


def test_corrections_revalidate_rejected_rows_and_keep_order_and_tags(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="Correction")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="broken\na.nl\nalso-broken"))
    rejected = batch.items.get(raw_domain="broken")
    rejected.tags = ["keep"]
    rejected.save(update_fields=["tags"])
    other = batch.items.get(raw_domain="also-broken")
    data = batches.correct_batch(
        batch_user.account,
        batch.id,
        [batches.CorrectionSchema(id=rejected.id, value="z.nl"), batches.CorrectionSchema(id=other.id, value="")],
    )
    batch = run_batch(data)
    assert tuple(batch.items.order_by("position").values_list("status", flat=True)) == ("valid", "valid", "removed"), (
        "Correction and deletion must retain the original input positions."
    )
    batches.confirm_batch(batch_user.account, batch.id)
    batch = run_batch({"id": batch.id})
    assert tuple(urllist.taggedurlinurllist_set.get(url__url="z.nl").tags.names()) == ("keep",), (
        "Correcting a spreadsheet domain must preserve its original tags."
    )


def test_spreadsheet_detects_swapped_columns_and_merges_duplicate_tags(batch_user):
    file = SimpleUploadedFile(
        "swapped.csv", b"Category / List,Tags,Domain\nA,one,z.nl\nA,two,z.nl\nA,,broken\nB,,a.nl\n"
    )
    batch = run_batch(batches.start_batch(batch_user, file=file))
    assert batch.status == "review", "Recognized headers should allow swapped Domain and Tags columns."
    assert not UrlList.objects.filter(account=batch_user.account).exists(), (
        "New lists must only be created after confirmation."
    )
    assert batch.items.get(status="valid", domain="z.nl").tags == ["one", "two"], (
        "Repeated domains must retain all supplied tags."
    )
    assert batch.items.get(status="invalid").row == 4, "Feedback must reference the original spreadsheet row."
    batches.confirm_batch(batch_user.account, batch.id)
    batch = run_batch({"id": batch.id})
    assert UrlList.objects.get(account=batch_user.account, name="A").urls.count() == 1, (
        "Each spreadsheet list must get its own domains."
    )
    assert UrlList.objects.get(account=batch_user.account, name="B").urls.count() == 1, (
        "A batch must support multiple lists."
    )


@pytest.mark.parametrize("content", [b"", b"Tags,Wrong\nx,y\n", b"Category / List,Domain\n"])
def test_empty_or_malformed_spreadsheets_have_persisted_actionable_errors(batch_user, content):
    batch = run_batch(batches.start_batch(batch_user, file=SimpleUploadedFile("bad.csv", content)))
    assert batch.status == "failed", "Bad files must end in a visible failure instead of a silent upload success."
    assert batch.message, "The user must receive an explanation of the spreadsheet failure."
    assert not batch.items.exists(), "Parsing failure must not leave a partly initialized batch."


def test_target_spreadsheet_upload_does_not_clear_existing_domains_or_tags(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="Keep")
    existing = Url.add("existing.nl")
    urllist.urls.add(existing)
    batches.add_tags_to_urls_in_urllist(existing, urllist, ["original"])
    file = SimpleUploadedFile("merge.csv", b"Domain,Tags\nexisting.nl,new\nz.nl,new\n")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, file=file))
    batches.confirm_batch(batch_user.account, batch.id)
    run_batch({"id": batch.id})
    assert urllist.urls.count() == 2, "A list upload must add to the existing list rather than replace its contents."
    assert set(urllist.taggedurlinurllist_set.get(url=existing).tags.names()) == {"original", "new"}, (
        "Existing tags must survive and incoming tags must be merged after confirmation."
    )


def test_failed_worker_can_resume_without_readding_completed_rows(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Resume")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="z.nl\na.nl"))
    batches.confirm_batch(batch_user.account, batch.id)
    original_add = Url.add

    def interrupted(domain):
        if domain == "a.nl":
            raise RuntimeError("Interrupted")
        return original_add(domain)

    monkeypatch.setattr(Url, "add", interrupted)
    batch = run_batch({"id": batch.id})
    assert batch.status == "failed" and urllist.urls.count() == 1, "Interruption must preserve already committed work."
    monkeypatch.setattr(Url, "add", original_add)
    batch = run_batch(batches.retry_batch(batch_user.account, batch.id))
    assert batch.status == "completed" and urllist.urls.count() == 2, "Resuming should process only the remaining rows."
    assert batch.items.filter(status="added").count() == 2, (
        "Previously added domains must retain their original outcomes."
    )


def test_duplicate_worker_delivery_does_not_restart_a_running_batch(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="Duplicate worker")
    data = batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="z.nl")
    DomainBatch.objects.filter(id=data["id"]).update(status="running", worker_token="first-worker")
    batch = run_batch(data)
    assert batch.worker_token == "first-worker" and not batch.items.exists(), (
        "Only one worker may claim a queued batch."
    )
    with pytest.raises(ApiError, match="still running"):
        batches.retry_batch(batch_user.account, batch.id)
    DomainBatch.objects.filter(id=batch.id).update(updated_on=now() - timedelta(minutes=20))
    batch = run_batch(batches.retry_batch(batch_user.account, batch.id))
    assert batch.status == "review", "A stale worker lease must allow explicit recovery."


def test_queue_outage_marks_the_batch_failed_and_returns_503(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="Queue")
    batches.process_domain_batch.send.side_effect = RuntimeError("Unavailable")
    with pytest.raises(batches.BatchQueueUnavailable):
        batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="z.nl")
    batch = DomainBatch.objects.get()
    assert batch.status == "failed", "Unscheduled work must be recoverable rather than remain queued forever."
    assert batch.message == batches.BatchQueueUnavailable.detail, "Queue failure must have a readable message."


@override_config(DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET=20000)
def test_text_accepts_ten_thousand_domains_without_a_synchronous_dns_check(batch_user, client):
    urllist = UrlList.objects.create(account=batch_user.account, name="Large")
    text = "\n".join(f"d{index}.example.nl" for index in range(10001))
    response = client.post(
        f"/api/v1/urllists/{urllist.id}/urls", json.dumps({"raw_urls": text}), content_type="application/json"
    )
    assert response.status_code == 202, "Large text batches must be accepted for background validation."
    assert DomainBatch.objects.get().raw_text == text, (
        "The entire input must reach the durable batch without truncation."
    )
    assert not DomainBatchItem.objects.exists(), "Request handling must not perform background parsing or DNS lookups."


def test_batch_api_is_account_scoped_and_returns_all_rejections(batch_user, client):
    urllist = UrlList.objects.create(account=batch_user.account, name="Feedback")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="broken\nalso-broken\nz.nl"))
    root = f"/api/v1/urllists/domain-batches/{batch.id}"
    response = client.get(root + "/rejections")
    assert response.status_code == 200, "The frontend must be able to retrieve all rejected input in one request."
    assert tuple(item["raw_domain"] for item in response.json()) == ("broken", "also-broken"), (
        "Feedback must contain only rejected rows in original input order, ready for local filtering and pagination."
    )
    foreign = Account.objects.create(name="Foreign")
    DomainBatch.objects.filter(id=batch.id).update(account=foreign)
    for suffix in ("", "/rejections"):
        assert client.get(root + suffix).status_code == 404, "A foreign batch must not reveal domains or progress."
    for suffix in ("/confirm", "/retry", "/corrections"):
        payload = {"corrections": [{"id": 1, "value": "x.nl"}]} if suffix == "/corrections" else {}
        assert client.post(root + suffix, json.dumps(payload), content_type="application/json").status_code == 404, (
            "A foreign account must not be able to mutate the batch."
        )


def test_dns_timeouts_become_per_domain_feedback(batch_user, monkeypatch):
    monkeypatch.setattr(batches, "has_a_or_aaaa", Mock(side_effect=Timeout))
    resolves, reason = batches.resolve_domain("example.nl")
    assert not resolves and "timed out" in reason, (
        "A DNS timeout must be actionable feedback rather than a stalled batch."
    )


def test_rejection_feedback_returns_more_than_ten_thousand_rows_without_truncating(batch_user, client):
    urllist = UrlList.objects.create(account=batch_user.account, name="Large feedback")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="accepted.nl"))
    statuses = ("invalid", "unresolvable", "limit")
    DomainBatchItem.objects.bulk_create(
        DomainBatchItem(
            batch=batch,
            position=index + 2,
            row=index + 2,
            raw_domain=f"rejected{index}.nl",
            list_name=urllist.name,
            status=statuses[index % len(statuses)],
        )
        for index in range(10_001)
    )
    response = client.get(f"/api/v1/urllists/domain-batches/{batch.id}/rejections")
    assert response.status_code == 200, "Large feedback lists must be returned in one successful response."
    rejected = response.json()
    assert len(rejected) == 10_001, "The API must not truncate feedback at a former page boundary."
    assert rejected[0]["raw_domain"] == "rejected0.nl" and rejected[-1]["raw_domain"] == "rejected10000.nl", (
        "All rejection types must retain input order while the accepted row stays excluded."
    )
    assert batch.items.count() == 10_002, "Retrieving feedback must never change accepted or rejected input."


def test_corrections_can_include_edits_from_more_than_two_frontend_pages(batch_user, client):
    urllist = UrlList.objects.create(account=batch_user.account, name="Many corrections")
    batch = run_batch(
        batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="\n".join(f"broken{row}" for row in range(101)))
    )
    corrections = [{"id": item.id, "value": f"corrected{item.row}.nl"} for item in batch.items.order_by("position")]
    response = client.post(
        f"/api/v1/urllists/domain-batches/{batch.id}/corrections",
        json.dumps({"corrections": corrections}),
        content_type="application/json",
    )
    assert response.status_code == 202, "Corrections retained across local pages must be accepted together."
    assert batch.items.filter(status="pending", raw_domain__startswith="corrected").count() == 101, (
        "Submitting corrections must retain every edit, including rows hidden by the current filter or page."
    )


@override_config(DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET=20000)
def test_large_batch_finishes_validation_and_truncates_in_input_order(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Large ordered import")
    text = "\n".join(f"d{index}.example.nl" for index in range(10001))
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls=text))
    assert batch.status == "review" and batch.processed == 10001, "Every row in a large batch must be validated."
    assert batch.items.filter(status="valid").count() == 10001, "Large batches must not lose or silently trim input."
    # A small output limit exercises truncation across hundreds of worker chunks.
    with override_config(DASHBOARD_MAXIMUM_DOMAINS_PER_LIST=3):
        dns = Mock(return_value=True)
        monkeypatch.setattr(batches, "has_a_or_aaaa", dns)
        batches.confirm_batch(batch_user.account, batch.id)
        batch = run_batch({"id": batch.id})
    assert batch.status == "completed", "Processing must continue through the entire batch after capacity is reached."
    assert set(urllist.urls.values_list("url", flat=True)) == {"d0.example.nl", "d1.example.nl", "d2.example.nl"}, (
        "Truncation must preserve supplied order rather than alphabetical order."
    )
    assert batch.items.filter(status="limit").count() == 9998, "Every truncated row needs a persisted outcome."
    assert dns.call_count <= batches.CHUNK_SIZE, "A full list must not cause DNS lookups for every overflow row."


def test_invalid_list_names_can_be_corrected_in_the_browser(batch_user):
    upload = SimpleUploadedFile("missing-list.csv", b"List,Domain,Tags\n,z.nl,keep\n")
    batch = run_batch(batches.start_batch(batch_user, file=upload))
    item = batch.items.get()
    assert item.status == "invalid", "A missing list name must be returned as editable row feedback."
    batch = run_batch(
        batches.correct_batch(
            batch_user.account, batch.id, [batches.CorrectionSchema(id=item.id, value="z.nl", list_name="Corrected")]
        )
    )
    assert batch.status == "review" and batch.items.get().status == "valid", "Corrected list names must be revalidated."
    batches.confirm_batch(batch_user.account, batch.id)
    run_batch({"id": batch.id})
    assert UrlList.objects.get(account=batch_user.account, name="Corrected").urls.count() == 1, (
        "The corrected row must reach the list named by the user."
    )


@pytest.mark.parametrize("extension", ["csv", "xlsx", "ods"])
def test_sample_spreadsheets_use_the_shared_validation_flow(batch_user, extension):
    from pathlib import Path

    path = Path(__file__).parent / "test spreadsheet uploads" / f"waterschappen.{extension}"
    batch = run_batch(batches.start_batch(batch_user, file=SimpleUploadedFile(path.name, path.read_bytes())))
    assert batch.status == "review", "Each supported sample spreadsheet must produce reviewable feedback."
    assert batch.items.filter(status="valid").count() == 27, (
        "All 27 distinct list/domain pairs in the samples must survive."
    )


def test_only_one_addition_per_account_can_be_confirmed(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="One at a time")
    first = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="z.nl"))
    second = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="a.nl"))
    batches.confirm_batch(batch_user.account, first.id)
    with pytest.raises(ApiError, match="Another batch"):
        batches.confirm_batch(batch_user.account, second.id)
    second.refresh_from_db()
    assert second.status == "review", "A scheduling conflict must leave the second preview available for confirmation."


def test_deleting_a_list_during_addition_stops_further_writes(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Deleted during import")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="z.nl\na.nl"))
    batches.confirm_batch(batch_user.account, batch.id)
    original_add = Url.add

    def delete_after_first_domain(domain):
        result = original_add(domain)
        UrlList.objects.filter(id=urllist.id).update(is_deleted=True)
        return result

    monkeypatch.setattr(Url, "add", delete_after_first_domain)
    batch = run_batch({"id": batch.id})
    assert batch.status == "failed", "An import must stop if its target list is deleted while processing."
    assert urllist.urls.count() == 1, "The worker must not continue writing domains using a cached list object."
    assert batch.items.get(domain="a.nl").status == "valid", "Unprocessed rows must retain their pending outcome."


def test_corrected_duplicate_merges_tags_only_after_confirmation(batch_user):
    upload = SimpleUploadedFile("corrected-tags.csv", b"List,Domain,Tags\nA,z.nl,first\nA,broken,second\n")
    batch = run_batch(batches.start_batch(batch_user, file=upload))
    batches.confirm_batch(batch_user.account, batch.id)
    batch = run_batch({"id": batch.id})
    rejected = batch.items.get(status="invalid")
    batch = run_batch(
        batches.correct_batch(batch_user.account, batch.id, [batches.CorrectionSchema(id=rejected.id, value="z.nl")])
    )
    urllist = UrlList.objects.get(account=batch_user.account, name="A")
    tagged = urllist.taggedurlinurllist_set.get(url__url="z.nl")
    assert set(tagged.tags.names()) == {"first"}, "Correcting input must not write tags before confirmation."
    batches.confirm_batch(batch_user.account, batch.id)
    run_batch({"id": batch.id})
    assert set(tagged.tags.names()) == {"first", "second"}, (
        "Corrected duplicate domains must retain their incoming tags."
    )
    assert urllist.urls.count() == 1, "Correcting a duplicate must not consume another list place."


@pytest.mark.parametrize("state", ["queued", "running", "review", "failed"])
def test_cancellation_is_immediate_idempotent_and_independent_of_the_broker(batch_user, client, state):
    urllist = UrlList.objects.create(account=batch_user.account, name="Cancel")
    batch = DomainBatch.objects.create(
        account=batch_user.account,
        user=batch_user,
        urllist=urllist,
        target_list=True,
        status=state,
        worker_token="crashed-worker",
        stage="addition",
        updated_on=now() - timedelta(hours=1),
    )
    batches.process_domain_batch.send.side_effect = RuntimeError("Broker unavailable")
    for _ in range(2):
        response = client.delete(f"/api/v1/urllists/domain-batches/{batch.id}")
        assert response.status_code == 204 and response.content == b"", (
            "Cancelling active or cancelled work must be idempotent."
        )
    batch.refresh_from_db()
    assert batch.status == "cancelled" and not batch.worker_token, (
        "Cancellation must invalidate the old worker immediately."
    )
    assert not batches.batch_summary(batch)["resumable"], "Cancelled batches must not be offered for retry."
    assert batches.process_domain_batch.send.call_count == 0, (
        "Stopping crashed work must not require a working task broker."
    )
    batches.process_domain_batch(batch.id)
    batch.refresh_from_db()
    assert batch.status == "cancelled", "A delayed or redelivered message must not restart cancelled work."


def test_cancel_rejects_completed_or_foreign_batches(batch_user, client):
    completed = DomainBatch.objects.create(account=batch_user.account, user=batch_user, status="completed")
    assert client.delete(f"/api/v1/urllists/domain-batches/{completed.id}").status_code == 409, (
        "Completed work must not be reclassified as cancelled."
    )
    foreign = DomainBatch.objects.create(account=Account.objects.create(name="Other"), user=batch_user)
    assert client.delete(f"/api/v1/urllists/domain-batches/{foreign.id}").status_code == 404, (
        "Another account must not be able to cancel this batch."
    )
    assert client.delete("/api/v1/urllists/domain-batches/999999").status_code == 404, (
        "Missing batches must return not found."
    )
    foreign.refresh_from_db()
    assert foreign.status == "queued", "A rejected foreign request must leave the batch unchanged."


def test_cancel_stops_validation_without_overwriting_terminal_state(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Cancel validation")
    data = batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="first.nl\nsecond.nl")
    original = Url.is_valid_url

    def cancel_second(domain):
        if domain == "second.nl":
            batches.cancel_batch(batch_user.account, data["id"])
        return original(domain)

    monkeypatch.setattr(Url, "is_valid_url", cancel_second)
    batch = run_batch(data)
    assert batch.status == "cancelled", (
        "Finishing a validation row must not replace cancellation with review or failure."
    )
    assert batch.items.get(position=2).status == "pending", (
        "Validation must stop before persisting a row after cancellation."
    )
    assert urllist.urls.count() == 0, "Cancelling validation must never add domains."


@pytest.mark.parametrize("overwrite", [False, True])
@pytest.mark.parametrize("worker_error", [False, True])
def test_cancellation_during_resolution_stops_writes_and_preserves_existing_list(
    batch_user, monkeypatch, overwrite, worker_error
):
    urllist = UrlList.objects.create(account=batch_user.account, name="Cancel during DNS")
    urllist.urls.add(Url.add("original.nl"))
    upload = SimpleUploadedFile("cancel.csv", b"Domain,Tags\nfirst.nl,one\nsecond.nl,two\n")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, file=upload))
    batches.confirm_batch(batch_user.account, batch.id, overwrite=overwrite, confirmation="overwrite")

    class CancellingPool:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def map(self, function, domains):
            for position, domain in enumerate(domains):
                if position == 1:
                    batches.cancel_batch(batch_user.account, batch.id)
                    if worker_error:
                        raise RuntimeError("Worker failed after cancellation")
                yield function(domain)

    monkeypatch.setattr(batches, "ThreadPoolExecutor", CancellingPool)
    batch = run_batch({"id": batch.id})
    assert batch.status == "cancelled", "Neither outstanding DNS results nor worker errors may undo cancellation."
    expected = {"original.nl"} if overwrite else {"original.nl", "first.nl"}
    assert set(urllist.urls.values_list("url", flat=True)) == expected, (
        "Merges must retain completed additions; cancelled replacements must retain the entire original list."
    )
    assert batch.items.get(domain="second.nl").status == "valid", (
        "No outcome may be written for rows after cancellation."
    )
    with pytest.raises(ApiError):
        batches.retry_batch(batch_user.account, batch.id)
    with pytest.raises(ApiError):
        batches.confirm_batch(batch_user.account, batch.id)


def test_cancellation_frees_the_account_for_another_batch(batch_user):
    urllist = UrlList.objects.create(account=batch_user.account, name="Free slot")
    first = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="first.nl"))
    second = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="second.nl"))
    batches.confirm_batch(batch_user.account, first.id)
    batches.cancel_batch(batch_user.account, first.id)
    accepted = batches.confirm_batch(batch_user.account, second.id)
    assert accepted["status"] == "queued", "Cancelled or crashed work must no longer block other additions."


def test_queue_failure_after_cancellation_does_not_revive_batch(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Queue cancellation")

    def cancel_then_fail(batch_id):
        batches.cancel_batch(batch_user.account, batch_id)
        raise RuntimeError("Queue unavailable")

    monkeypatch.setattr(batches.process_domain_batch, "send", cancel_then_fail)
    with pytest.raises(batches.BatchQueueUnavailable):
        batches.start_batch(batch_user, urllist_id=urllist.id, raw_urls="first.nl")
    assert DomainBatch.objects.get().status == "cancelled", "A late broker failure must preserve the cancelled state."


@pytest.mark.parametrize("confirmation", ["overwrite", "overschrijven"])
def test_overwrite_replaces_membership_and_tags_only_after_success(batch_user, confirmation):
    urllist = UrlList.objects.create(account=batch_user.account, name="Replace")
    existing = Url.add("existing.nl")
    urllist.urls.add(existing, Url.add("remove.nl"))
    batches.add_tags_to_urls_in_urllist(existing, urllist, ["old"])
    other = UrlList.objects.create(account=batch_user.account, name="Keep other list")
    other.urls.add(existing)
    batches.add_tags_to_urls_in_urllist(existing, other, ["other"])
    upload = SimpleUploadedFile("replacement.csv", b"Domain,Tags\nexisting.nl,new\nz.nl,incoming\n")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, file=upload))
    batches.confirm_batch(batch_user.account, batch.id, overwrite=True, confirmation=confirmation)
    assert set(urllist.urls.values_list("url", flat=True)) == {"existing.nl", "remove.nl"}, (
        "Confirming overwrite must leave current contents intact until replacement processing succeeds."
    )
    batch = run_batch({"id": batch.id})
    assert batch.status == "completed", "A successfully prepared replacement must complete atomically."
    assert set(urllist.urls.values_list("url", flat=True)) == {"existing.nl", "z.nl"}, (
        "Only spreadsheet domains should remain."
    )
    assert set(urllist.taggedurlinurllist_set.get(url=existing).tags.names()) == {"new"}, (
        "Overwrite must replace list-specific tags."
    )
    assert set(other.taggedurlinurllist_set.get(url=existing).tags.names()) == {"other"}, (
        "Other lists and their tags must be retained."
    )
    assert batches.batch_summary(batch)["lists"] == [{"id": urllist.id, "name": "Replace"}], (
        "Completed batches must expose the destination list for frontend navigation."
    )


@pytest.mark.parametrize("confirmation", ["", "replace", "overwrit"])
def test_overwrite_requires_typed_confirmation(batch_user, client, confirmation):
    urllist = UrlList.objects.create(account=batch_user.account, name="Explicit overwrite")
    urllist.urls.add(Url.add("keep.nl"))
    upload = SimpleUploadedFile("replacement.csv", b"Domain\nz.nl\n")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, file=upload))
    response = client.post(
        f"/api/v1/urllists/domain-batches/{batch.id}/confirm",
        json.dumps({"overwrite": True, "confirmation": confirmation}),
        content_type="application/json",
    )
    assert response.status_code == 400, "The API must enforce typed consent, independently of the frontend switch."
    batch.refresh_from_db()
    assert batch.status == "review" and not batch.overwrite, "Invalid confirmation must leave the preview available."
    assert urllist.urls.count() == 1, "Unconfirmed replacement must not change the list."


def test_failed_replacement_keeps_original_contents_and_can_resume(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Atomic overwrite")
    urllist.urls.add(Url.add("original.nl"))
    upload = SimpleUploadedFile("replacement.csv", b"Domain\nfirst.nl\nsecond.nl\n")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, file=upload))
    batches.confirm_batch(batch_user.account, batch.id, overwrite=True, confirmation="overwrite")
    original = Url.add

    def fail_second(domain):
        if domain == "second.nl":
            raise RuntimeError("Write failed")
        return original(domain)

    monkeypatch.setattr(Url, "add", fail_second)
    batch = run_batch({"id": batch.id})
    assert batch.status == "failed", "A failed replacement transaction must report a recoverable failure."
    assert set(urllist.urls.values_list("url", flat=True)) == {"original.nl"}, (
        "Partial replacement writes must roll back."
    )
    assert batch.items.filter(status="prepared").count() == 2, "Prepared results must remain available for recovery."
    monkeypatch.setattr(Url, "add", original)
    batch = run_batch(batches.retry_batch(batch_user.account, batch.id))
    assert batch.status == "completed" and urllist.urls.count() == 2, "Resuming must commit the complete replacement."


def test_unresolvable_replacement_never_empties_the_existing_list(batch_user, monkeypatch):
    urllist = UrlList.objects.create(account=batch_user.account, name="Keep on DNS rejection")
    urllist.urls.add(Url.add("keep.nl"))
    upload = SimpleUploadedFile("replacement.csv", b"Domain\nno-dns.nl\n")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, file=upload))
    batches.confirm_batch(batch_user.account, batch.id, overwrite=True, confirmation="overwrite")
    monkeypatch.setattr(batches, "resolve_domain", lambda domain: (False, "No DNS records"))
    batch = run_batch({"id": batch.id})
    assert batch.status == "failed", "An entirely rejected replacement must have explicit feedback."
    assert set(urllist.urls.values_list("url", flat=True)) == {"keep.nl"}, (
        "DNS failure must not empty the existing list."
    )


@pytest.mark.parametrize("initial_overwrite", [False, True])
def test_corrections_after_processing_preserve_prior_additions(batch_user, initial_overwrite):
    urllist = UrlList.objects.create(account=batch_user.account, name="Correct a processed spreadsheet")
    upload = SimpleUploadedFile("replacement.csv", b"Domain\nfirst.nl\nbroken\n")
    batch = run_batch(batches.start_batch(batch_user, urllist_id=urllist.id, file=upload))
    batches.confirm_batch(batch_user.account, batch.id, overwrite=initial_overwrite, confirmation="overwrite")
    batch = run_batch({"id": batch.id})
    rejected = batch.items.get(status="invalid")
    batch = run_batch(
        batches.correct_batch(
            batch_user.account, batch.id, [batches.CorrectionSchema(id=rejected.id, value="second.nl")]
        )
    )
    with pytest.raises(ApiError) as error:
        batches.confirm_batch(batch_user.account, batch.id, overwrite=True, confirmation="overwrite")
    assert error.value.status_code == 409, (
        "Reprocessing only corrected rows must never replace prior spreadsheet additions."
    )
    batch = run_batch(batches.confirm_batch(batch_user.account, batch.id))
    assert batch.status == "completed" and not batch.overwrite, "Corrected domains should be added normally."
    assert set(urllist.urls.values_list("url", flat=True)) == {"first.nl", "second.nl"}, (
        "Correcting a rejected row must retain domains already imported from the same spreadsheet."
    )


@pytest.mark.parametrize("pending_only", [False, True])
def test_pending_history_retains_actionable_statuses_and_respects_account_and_list(batch_user, client, pending_only):
    urllist = UrlList.objects.create(account=batch_user.account, name="Pending imports")
    other_list = UrlList.objects.create(account=batch_user.account, name="Other list")
    foreign = Account.objects.create(name="Foreign imports")
    statuses = ("queued", "running", "review", "failed", "completed", "cancelled")
    for status in statuses:
        DomainBatch.objects.create(account=batch_user.account, user=batch_user, urllist=urllist, status=status)
    DomainBatch.objects.create(account=batch_user.account, user=batch_user, urllist=other_list, status="review")
    DomainBatch.objects.create(account=foreign, user=batch_user, urllist=urllist, status="review")
    response = client.get("/api/v1/urllists/domain-batches", {"urllistId": urllist.id, "pendingOnly": pending_only})
    assert response.status_code == 200, "Import history must support an explicit pending-only query."
    expected = statuses[:4] if pending_only else statuses
    assert tuple(entry["status"] for entry in response.json()) == tuple(reversed(expected)), (
        "Pending history must retain failed/review/active imports, and every query must respect account and list scope."
    )
    full_history = client.get("/api/v1/urllists/domain-batches").json()
    assert len(full_history) == 7, (
        "The unfiltered upload-page history must include both finished and cancelled imports."
    )


def test_pending_history_filters_before_the_recent_history_limit(batch_user, client):
    urllist = UrlList.objects.create(account=batch_user.account, name="Older pending import")
    pending = DomainBatch.objects.create(account=batch_user.account, user=batch_user, urllist=urllist, status="review")
    DomainBatch.objects.bulk_create(
        DomainBatch(account=batch_user.account, user=batch_user, urllist=urllist, status="completed") for _ in range(35)
    )
    response = client.get("/api/v1/urllists/domain-batches", {"urllistId": urllist.id, "pendingOnly": True})
    assert response.status_code == 200, "Older pending imports must remain accessible after many completed uploads."
    assert [entry["id"] for entry in response.json()] == [pending.id], (
        "Completed records must be removed before limiting recent results so open work is not hidden."
    )
