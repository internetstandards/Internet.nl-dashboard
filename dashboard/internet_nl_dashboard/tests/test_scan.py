from django.utils import timezone

from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan,
                                                    AccountInternetNLScanLog, UrlList)
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import update_state


def test_update_state(db):

    account = Account()
    account.save()

    urllist = UrlList(**{'name': '', 'account': account})
    urllist.save()

    scan = AccountInternetNLScan()
    scan.urllist = urllist
    scan.account = account
    scan.save()

    update_state("new", scan)

    # A situation has occurred where the log was already in the next step, but the scan state itself was
    # at the old step. This caused the scan to block: as the logic was that if the log is in the correct / new state
    # it was assumed the scan was also in that state. This is fixed and tested below.

    scanlog = AccountInternetNLScanLog()
    scanlog.scan = scan
    scanlog.at_when = timezone.now()
    scanlog.state = "out of sync"
    scanlog.save()

    update_state("out of sync", scan)

    my_scan = AccountInternetNLScan.objects.all().first()
    assert my_scan.state == "out of sync"

    # new, out of sync, out of sync
    # The last duplicate is stored to make it clear something went wrong. There is nothing 'attached' to the log
    # other than understanding the process in case of weird situations.
    assert AccountInternetNLScanLog.objects.all().count() == 3

    # make sure the amount of log info does not grow if things are the same
    update_state("out of sync", my_scan)
    update_state("out of sync", my_scan)
    update_state("out of sync", my_scan)
    assert AccountInternetNLScanLog.objects.all().count() == 3
