import json
from datetime import datetime, timezone

from celery import group
from websecmap.scanners.scanner.dns_endpoints import has_a_or_aaaa, has_soa

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.logic.domains import _add_to_urls_to_urllist_nicer
from dashboard.internet_nl_dashboard.models import Account, SubdomainDiscoveryScan, UrlList


# UI Operation
def request_scan(account: Account, urllist_id: int):
    urllist = UrlList.objects.all().filter(account=account, id=urllist_id).first()
    if not urllist:
        return operation_response(error=True, message="list_does_not_exist")

    # Can only start a scan when the previous one finished:
    last_scan = SubdomainDiscoveryScan.objects.all().filter(urllist=urllist_id).last()
    if not last_scan:
        scan = SubdomainDiscoveryScan()
        scan.urllist = urllist
        scan.save()
        update_state(scan.id, "requested")
        return scan_status(account, urllist_id)

    if last_scan.state in ['requested', 'scanning']:
        return scan_status(account, urllist_id)

    scan = SubdomainDiscoveryScan()
    scan.urllist = urllist
    scan.save()
    update_state(scan.id, "requested")

    return scan_status(account, urllist_id)


def scan_status(account: Account, urllist_id: int):
    urllist = UrlList.objects.all().filter(account=account, id=urllist_id).first()
    if not urllist:
        return operation_response(error=True, message="list_does_not_exist")

    scan = SubdomainDiscoveryScan.objects.all().filter(urllist=urllist).last()
    if not scan:
        return operation_response(error=True, message="not_scanned_at_all")

    return {'success': True, 'error': False, 'state': scan.state, 'state_message': scan.state_message,
            'state_changed_on': scan.state_changed_on,
            'domains_discovered': json.loads(scan.domains_discovered) if scan.domains_discovered else {}}


# Process
@app.task(queue="storage")
def progress_subdomain_discovery_scans():
    scans = SubdomainDiscoveryScan.objects.all().filter(state="requested")

    tasks = []
    for scan in scans:
        update_state(scan.id, "scanning")
        tasks.append(group(perform_subdomain_scan.si(scan.id) | update_state.si(scan.id, "finished")))

    # todo: check for timeouts and retry...
    return group(tasks)


@app.task(queue="storage")
def update_state(scan_id: int, new_state: str, message: str = ""):

    scan = SubdomainDiscoveryScan.objects.all().filter(id=scan_id).first()
    if not scan:
        return

    scan.state = new_state
    if message:
        scan.state_message = message
    scan.state_changed_on = datetime.now(timezone.utc)
    scan.save()


# todo: does scanning queue exist in internet.nl dashboard environment?
@app.task(queue="storage")
def perform_subdomain_scan(scan_id: int) -> None:
    # This is different than the dns_endpoints scanner, because that runs on URLS that already are in the database.
    # In this case we want to check if the url exists BEFORE adding it to the database.
    # Web = DNS_A_AAAA and for mail = DNS_SOA
    # The urls could already be in the database and should then be connected to the current list, reuse existing code
    # Wildcards don't matter for now.

    scan = SubdomainDiscoveryScan.objects.all().filter(id=scan_id).first()
    if not scan:
        return

    urllist = scan.urllist

    try:
        toplevel_domains = urllist.urls.filter(computed_subdomain="")
        domains_to_check = [f"www.{url.url}" for url in toplevel_domains]

        urls_to_add = []
        # This can take a while because it's synchronous. Done that way to see what urls have been added.
        for domain in domains_to_check:
            # don't know which one is saved here, so just testing for both mail and mail_dashboard
            if urllist.scan_type in ["mail", "mail_dashboard", "all"]:
                if has_soa(domain):
                    urls_to_add.append(domain)

            if urllist.scan_type in ["web", "all"]:
                if has_a_or_aaaa(domain):
                    urls_to_add.append(domain)

        # could have been both mail or web in case of all...
        urls_to_add = list(set(urls_to_add))
        counters = _add_to_urls_to_urllist_nicer(account=urllist.account, current_list=urllist, urls=urls_to_add)
        scan.domains_discovered = json.dumps(counters)
        scan.save()
    except Exception as my_exception:  # pylint: disable=broad-except
        # This is run in a task where there is only exception info in sentry or the task itself.
        update_state(scan, "error", str(my_exception))
        # Still send it to sentry and crash
        raise Exception from my_exception  # pylint: disable=broad-exception-raised
