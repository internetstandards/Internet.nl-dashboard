from dashboard.internet_nl_dashboard.scanners import scan_internet_nl_per_account
from websecmap.scanners.scanner import dns_endpoints

# explicitly declare the imported modules as this modules 'content', prevents pyflakes issues
# somehow dns_endpoints as well as a bunch of other scanners from wsm are not autodiscovered here.
# We don't need them all, only dns_endpoints.
__all__ = [scan_internet_nl_per_account, dns_endpoints]
