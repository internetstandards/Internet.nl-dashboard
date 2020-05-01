import logging
import os

import requests
from django.core.management.base import BaseCommand
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__package__)

API_URL = "https://batch.internet.nl/api/batch/v1.1/mail/"


# Docs: github.com/NLnetLabs/Internet.nl/blob/new_forumstandaardisatie_custom_view/documentation/batch_http_api.md
class Command(BaseCommand):
    help = 'Very simple test to see if the internet.nl API is behaving correctly.'

    def handle(self, *args, **options):
        submit_scan(API_URL)


def submit_scan(api_url):

    # set -x INTERNET_NL_API_USERNAME username
    username = os.environ.get('INTERNET_NL_API_USERNAME', '')
    # set -x INTERNET_NL_API_PASSWORD password
    password = os.environ.get('INTERNET_NL_API_PASSWORD', '')

    if not username or not password:
        log.error(f"No username or password set in environment. Set them using "
                  f"'set -x INTERNET_NL_API_USERNAME username' and  'set -x INTERNET_NL_API_PASSWORD password'.")

    """
    POST /api/batch/v1.0/web/ HTTP/1.1
    {
        "name": "My web test",
        "domains": ["nlnetlabs.nl", "www.nlnetlabs.nl", "opennetlabs.nl", "www.opennetlabs.nl"]
    }
    """
    data = {"name": "test scan", "domains": ["nlnetlabs.nl", "www.nlnetlabs.nl", "opennetlabs.nl", "ford.nl", "nu.nl"]}

    answer = requests.post(api_url, json=data,
                           auth=HTTPBasicAuth(username, password), timeout=(300, 300))
    log.debug(f"Received answer from internet.nl: {answer.content}")
    log.debug("Request the above url in your browser.")

    answer = answer.json()
    repr(answer)
