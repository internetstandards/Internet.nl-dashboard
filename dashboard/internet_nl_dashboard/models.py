from django.contrib.auth.models import User
from django.db import models
from websecmap.organizations.models import Url


class Account(models.Model):
    name = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text=""
    )

    enable_logins = models.BooleanField(
        blank=True,
        null=True,
        default=False,
        help_text="Inactive accounts cannot be logged-in to."
    )

    internet_nl_api_username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Internet.nl API Username"
    )

    # todo: encrypt the password field on save, and retrieve an unencrypted version, where store keys etc...
    internet_nl_api_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="New values will automatically be encrypted."
    )

    def __str__(self):
        return self.name


class DashboardUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

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
