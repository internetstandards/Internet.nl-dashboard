from datetime import datetime

from django.test import Client
from freezegun import freeze_time

from dashboard.internet_nl_dashboard.models import Account, UrlList, UrlListReport


def test_get_publicly_shared_lists_per_account(db):
    with freeze_time("2020-01-01"):

        c = Client()

        # todo: perhaps mandate that a list-id is given, and perhaps that the list id has to be a guid.
        # no content no crash
        response = c.get('/data/report/public/lists/all/account/1/')
        assert response.content == b'[]'

        # create a list with some reports
        account = Account.objects.create(name="share_account")
        urllist = UrlList.objects.create(name="share_url_list", account=account, enable_report_sharing_page=True)
        urllistreport = UrlListReport.objects.create(
            urllist=urllist, report_type="web", at_when=datetime(2020, 1, 1), is_publicly_shared=True
        )

        expected_response = [
            {
                'list_id': urllist.id,
                'list_name': urllist.name,
                'number_of_reports': 1,
                'reports': [
                    {
                        'id': urllistreport.id,
                        'at_when': '2020-01-01T00:00:00Z',
                        'report_type': "web",
                        "has_public_share_code": False,
                        "average_internet_nl_score": 0.0,
                        "public_report_code": '',
                        'total_urls': 0,
                        'urllist__name': urllist.name
                    }
                ]
            }
        ]

        response = c.get(f'/data/report/public/lists/all/account/{account.id}/')
        assert response.status_code == 200
        assert response.json() == expected_response

        # non existing list:
        response = c.get(f'/data/report/public/lists/781263187/account/{account.id}/')
        assert response.content == b'[]'

        # non existing account:
        response = c.get(f'/data/report/public/lists/{urllist.id}/account/781263187/')
        assert response.content == b'[]'

        response = c.get(f'/data/report/public/lists/{urllist.id}/account/{account.id}/')
        assert response.status_code == 200
        assert response.json() == expected_response
