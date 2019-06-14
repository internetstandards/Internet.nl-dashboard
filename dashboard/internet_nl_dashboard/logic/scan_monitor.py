from datetime import timedelta
from typing import List

from django.utils import timezone

from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlListReport


# todo: probably this is much easier with django rest framework? (perhaps not conceptually)
def get_running_scans(account: Account) -> List:

    scans = AccountInternetNLScan.objects.all().filter(
        account=account,
        urllist__is_deleted=False
    ).order_by('-pk')[0:30].select_related(
        'urllist', 'account', 'scan'
    )

    response = []
    for scan in scans:
        # nested query, should be optimized, prefetch doesn't work here as it's one line down... for 30 queries
        # it's probably fine but far from ideal.

        last_report_id = None
        if scan.scan.finished_on:
            # first report within the next day

            last_report = UrlListReport.objects.all().filter(
                urllist=scan.urllist,
                # We can expect a report to be ready 24 hours after the scan has finished (?)
                # Otherwise maybe just get the latest scan for the urllist?
                # reports are stored at the last possible moment of the day. So every day there is at max 1 report.
                # If a scan if finished at exactly 00:00, the next report will be stored at 23:59:59 ...
                at_when__lte=scan.scan.finished_on + timedelta(hours=24),
                at_when__gte=scan.scan.finished_on
            ).order_by('-id').only('id').first()

            if last_report:
                last_report_id = last_report.id

        if scan.scan.finished:
            runtime = scan.scan.finished_on - scan.scan.started_on
        else:
            runtime = timezone.now() - scan.scan.started_on

        runtime = runtime.total_seconds() * 1000

        response.append({
            'id': scan.id,
            # mask that there is a mail_dashboard variant.
            'type': "web" if scan.scan.type == "web" else "mail",
            'started': scan.scan.started,
            'started_on': scan.scan.started_on,
            'finished': scan.scan.finished,
            'finished_on': scan.scan.finished_on,
            'status_url': scan.scan.status_url,
            'message': scan.scan.friendly_message,
            'success': scan.scan.success,
            'list': scan.urllist.name,
            'list_id': scan.urllist.id,
            'last_check': scan.scan.last_check,
            'runtime': runtime,
            'last_report_id': last_report_id,
        })

    return response
