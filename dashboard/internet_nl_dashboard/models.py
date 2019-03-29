import logging

import requests
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from requests.auth import HTTPBasicAuth

from websecmap.organizations.models import Url
from websecmap.scanners.models import InternetNLScan

log = logging.getLogger(__package__)

CREDENTIAL_CHECK_URL = "https://batch.internet.nl/api/"


class Account(models.Model):
    """
    An account is the entity that start scans. Multiple people can manage the account.
    """

    name = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text=""
    )

    enable_scans = models.BooleanField(
        default=True,
    )

    internet_nl_api_username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Internet.nl API Username"
    )

    internet_nl_api_password = models.BinaryField(
        blank=True,
        null=True,
        help_text="New values will automatically be encrypted.",
        editable=True
    )

    can_connect_to_internet_nl_api = models.BooleanField(
        default=False
    )

    """
    These password methods allow you to interact with encryption as if it were just storing and retrieving strings.
    See test_password_storage for example usage.
    """
    @staticmethod
    def encrypt_password(password):

        log.debug(password)

        f = Fernet(settings.FIELD_ENCRYPTION_KEY)
        return f.encrypt(password.encode())

    @staticmethod
    def connect_to_internet_nl_api(username: str, password: str):
        # This makes a connection to the internet.nl dashboard using .htaccess authentication.
        try:
            response = requests.get(
                CREDENTIAL_CHECK_URL,
                auth=HTTPBasicAuth(username, password),
                # a massive timeout for a large file.
                timeout=(5, 5)
            )

            # Any status code means the account is not valid.
            if response.status_code != 200:
                return False

            return True
        except requests.exceptions.ConnectionError:
            return False

    def decrypt_password(self):

        if not self.internet_nl_api_password:
            raise ValueError('Password was not set.')

        if not type(self.internet_nl_api_password) is bytes:
            raise ValueError('Password was not encrypted, cannot retrieve unencrypted passwords. Encrypt it first.')

        f = Fernet(settings.FIELD_ENCRYPTION_KEY)
        return f.decrypt(self.internet_nl_api_password).decode('utf-8')

    def __str__(self):
        return "%s" % self.name


class DashboardUser(models.Model):
    """
    This connects auth.User to a user that is used in the Dashboard. It is common practice to extend auth.Model with a
    one to one relation with an extended model.
    An additional benefit/feature is that we can easily switch what user is connected to what account.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
    )

    notes = models.TextField(
        max_length=800,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s/%s" % (self.account, self.user)


class UrlList(models.Model):
    """
    This is a list of urls that will be scanned on internet.nl.
    This list will be extended with things like: 'what should be scanned (mail / web)'. What to show on the dashboard.
    """

    name = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Name of the UrlList, for example name of the organization in it."
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text="Who owns and manages this urllist."
    )

    urls = models.ManyToManyField(
        Url,
        blank=True,
        related_name='urls_in_dashboard_list'
    )

    enable_scans = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return "%s/%s" % (self.account, self.name)


class AccountInternetNLScan(models.Model):
    """
    We've explicitly not declared the N-to-N on scan or account. This is the N to N between them. When a new scan is
    created the UrlList serves as extra data.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
    )

    scan = models.ForeignKey(
        InternetNLScan,
        on_delete=models.CASCADE,
    )

    urllist = models.ForeignKey(
        UrlList,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )


class UploadLog(models.Model):
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The original filename of the file that has been uploaded. Django appends a random string if the "
                  "file already exists. This is a reconstruction of the original filename and may not be 100% accurate."
    )

    internal_filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Generated filename by Django. This can be used to find specific files for debugging purposes."
    )

    status = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="If the upload was successful or not. Might contain 'success' or 'error'."
    )

    message = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="This message gives more specific information about what happened. For example, it might be the "
                  "case that a file has been rejected because it had the wrong filetype etc."
    )

    upload_date = models.DateTimeField(
        blank=True,
        null=True
    )

    filesize = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Gives an indication if your local file has changed (different size). The size is in bytes."
    )

    user = models.ForeignKey(
        DashboardUser,
        on_delete=models.CASCADE,
        help_text="What user performed this upload.",
        blank=True,
        null=True
    )
