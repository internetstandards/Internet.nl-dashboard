import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.models import UrlList
import requests
from requests.auth import HTTPBasicAuth
import os

log = logging.getLogger(__package__)

API_URL = "https://batch.internet.nl/api/batch/v1.1/mail/"

# set INTERNET_NL_API_USERNAME username
USERNAME = os.environ.get('INTERNET_NL_API_USERNAME', '')
# set INTERNET_NL_API_PASSWORD password
PASSWORD = os.environ.get('INTERNET_NL_API_PASSWORD', '')


# Docs: github.com/NLnetLabs/Internet.nl/blob/new_forumstandaardisatie_custom_view/documentation/batch_http_api.md
class Command(BaseCommand):
    help = 'Very simple test to see if the internet.nl API is behaving correctly.'

    def handle(self, *args, **options):
        """
        POST /api/batch/v1.0/web/ HTTP/1.1
        {
            "name": "My web test",
            "domains": ["nlnetlabs.nl", "www.nlnetlabs.nl", "opennetlabs.nl", "www.opennetlabs.nl"]
        }
        """
        data = {"name": "test scan", "domains": ["nlnetlabs.nl", "www.nlnetlabs.nl", "opennetlabs.nl"]}
        answer = requests.post(API_URL, json=data,
                               auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=(300, 300))
        log.debug("Received answer from internet.nl: %s" % answer.content)

        answer = answer.json()
        repr(answer)
