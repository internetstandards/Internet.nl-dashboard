from datetime import datetime, timezone

from django.test import Client
from freezegun import freeze_time

from dashboard.internet_nl_dashboard.models import Account, UrlList, UrlListReport


def test_get_publicly_shared_lists_per_account(db):
    with freeze_time("2020-01-01"):
        c = Client()

        # todo: perhaps mandate that a list-id is given, and perhaps that the list id has to be a guid.
        # no content no crash
        response = c.get("/data/public/account/1/lists/all")
        assert response.content == b"[]"

        # create a list with some reports
        account = Account.objects.create(name="share_account")
        urllist = UrlList.objects.create(name="share_url_list", account=account, enable_report_sharing_page=True)
        urllistreport = UrlListReport.objects.create(
            urllist=urllist,
            report_type="web",
            at_when=datetime(2020, 1, 1, tzinfo=timezone.utc),
            is_publicly_shared=True,
        )

        expected_response = [
            {
                "account": {"public_name": ""},
                "list": {
                    "id": urllist.id,
                    "name": urllist.name,
                    "scan_type": "web",
                    "automatically_share_new_reports": False,
                    "automated_scan_frequency": "disabled",
                },
                "number_of_reports": 1,
                "reports": [
                    {
                        "id": urllistreport.id,
                        # todo: this used to be "2020-01-01T00:00:00Z", does django ninja not have timezone support?
                        "at_when": "2020-01-01T00:00:00+00:00",
                        "report_type": "web",
                        "has_public_share_code": False,
                        "average_internet_nl_score": 0.0,
                        "public_report_code": "",
                        "total_urls": 0,
                        "urllist__name": urllist.name,
                    }
                ],
            }
        ]

        response = c.get(f"/data/public/account/{account.id}/lists/all")

        # remove randomness:
        assert response.status_code == 200
        json_data = response.json()
        json_data[0]["reports"][0]["public_report_code"] = ""
        print(json_data)
        assert json_data == expected_response

        # non existing list:
        response = c.get(f"/data/public/account/{account.id}/lists/781263187")
        assert response.content == b"[]"

        # non existing account:
        response = c.get(f"/data/public/account/781263187/lists/{urllist.id}")
        assert response.content == b"[]"

        response = c.get(f"/data/public/account/{account.id}/lists/{urllist.id}")
        json_data = response.json()
        json_data[0]["reports"][0]["public_report_code"] = ""
        assert json_data == expected_response
        assert response.status_code == 200
