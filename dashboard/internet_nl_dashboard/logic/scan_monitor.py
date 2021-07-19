from typing import List

from constance import config
from django.utils import timezone

from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan,
                                                    AccountInternetNLScanLog)


def get_scan_monitor_data(account: Account) -> List:
    scans = AccountInternetNLScan.objects.all().filter(
        account=account,
        urllist__is_deleted=False
    ).order_by('-pk')[0:30].select_related(
        'urllist', 'scan', 'report'
    ).only(
        'id',
        'state',
        'started_on',
        'finished_on',

        'scan__type',
        'scan__id',
        'scan__last_state_check',

        'urllist_id',
        'urllist__name',

        'report__id'
    )

    response = []
    for scan in scans:
        last_report_id = scan.report.id if scan.state == "finished" else None
        runtime = (scan.finished_on if scan.state == "finished" else timezone.now()) - scan.started_on
        runtime = runtime.total_seconds() * 1000

        logs = AccountInternetNLScanLog.objects.all().filter(scan=scan).only('at_when', 'state').order_by('-at_when')
        log_messages = [{'at_when': log.at_when, 'state': log.state} for log in logs]

        response.append({
            'id': scan.id,
            'state': scan.state,

            # mask that there is a mail_dashboard variant.
            'type': "web" if scan.scan.type == "web" else "mail",
            'started': True,
            'started_on': scan.started_on,
            'finished': scan.finished,
            'finished_on': scan.finished_on,
            'status_url': f"{config.INTERNET_NL_API_URL}/requests/{scan.scan.scan_id}",
            'message': scan.state,
            'success': scan.finished,
            'list': scan.urllist.name,
            'list_id': scan.urllist.id,
            'last_check': scan.scan.last_state_check,
            'runtime': runtime,
            'last_report_id': last_report_id,

            'log': log_messages
        })

    return response
