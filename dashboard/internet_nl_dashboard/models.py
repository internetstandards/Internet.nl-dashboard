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


# todo: should we allow a download of the file (if still available?)
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
