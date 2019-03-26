from typing import List
from dashboard.internet_nl_dashboard.models import Account
from websecmap.scanners.models import InternetNLScan


# todo: probably this is much easier with django rest framework? (perhaps not conceptually)
def get_running_scans(account: Account) -> List:

    scans = InternetNLScan.objects.all().filter(accountinternetnlscan__account=account)

    response = []
    for scan in scans:
        response.append({
            'id': scan.id,
            'type': scan.type,
            'started': scan.started,
            'started_on': scan.started_on,
            'finished': scan.finished,
            'finished_on': scan.finished_on,
            'status_url': scan.status_url,
            'message': scan.message,
            'success': scan.succes,
        })

    return response
