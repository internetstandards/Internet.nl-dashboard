"""
Run these tests with tox -e test -- -k test_translation
"""
import json
from pathlib import Path

import requests
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, InternetNLScan

from dashboard.internet_nl_dashboard.management.commands.retroactive_import import \
    retroactively_import
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan

path = Path(__file__).parent


def file_get_contents(filepath):
    with open(filepath, 'r') as content_file:
        return content_file.read()


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code
            self.json = lambda: json.loads(self.content)

    return MockResponse(
        file_get_contents(f'{path}/retroactive import/f95466dfd1de42ebbe809d12145f3fe0.json').encode(), 200)


# pytest mock fixtures overwrite the db signature, i mean... why?!
def test_retroactive_import(db, monkeypatch):
    monkeypatch.setattr(requests, 'get', mocked_requests_get)

    account = Account()
    account.id = 2
    account.name = "test"
    account.internet_nl_api_username = "test"
    account.internet_nl_api_password = account.encrypt_password("test")
    account.save()

    retroactively_import(
        {'account_id': account.id, 'report_id': 'e738da28c0724e188dc808580fdcdf0e', 'scan_type': 'web'})

    assert Url.objects.all().count() == 18
    assert Endpoint.objects.all().count() == 18
    assert InternetNLScan.objects.all().count() == 1
    assert AccountInternetNLScan.objects.all().count() == 1
