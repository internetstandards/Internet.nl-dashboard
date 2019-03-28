from typing import List

from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan


# todo: probably this is much easier with django rest framework? (perhaps not conceptually)
def get_running_scans(account: Account) -> List:

    scans = AccountInternetNLScan.objects.all().filter(account=account).order_by('-pk')[0:30].select_related(
        'urllist', 'account', 'scan')

    response = []
    for scan in scans:

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
            'list': scan.urllist.name
        })

    return response
