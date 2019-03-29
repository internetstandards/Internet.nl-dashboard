from modulefinder import Module
from typing import List

from dashboard.internet_nl_dashboard.scanners import scan_internet_nl_per_account

# explicitly declare the imported modules as this modules 'content', prevents pyflakes issues
__all__: List[Module] = [scan_internet_nl_per_account]
