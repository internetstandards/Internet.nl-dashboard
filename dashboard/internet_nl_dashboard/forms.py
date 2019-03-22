import logging

from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError

from dashboard.internet_nl_dashboard.models import Account, DashboardUser

log = logging.getLogger(__package__)


class InstantAccountAddForm(forms.Form):
    """
    This form can instantly create accounts to match the internet.nl API. This saves some time setting up the
    site for the first time, not having to go through the admin site and do too much repetitive work.
    """

    def __init__(self, *args, **kwargs):
        super(InstantAccountAddForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        label="Username",
        required=True,
        max_length=200
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        required=True,
        max_length=1000
    )

    def clean(self):
        # can't create a username or account that already exists.
        # There is no sensible password policy for this user.

        cleaned_data = super().clean()

        username = cleaned_data.get("username")

        if User.objects.all().filter(username=username).exists():
            raise ValidationError('User with this username already exists.')

        if Account.objects.all().filter(name=username).exists():
            raise ValidationError('Account with this username already exists.')

    def save(self):

        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = User(**{'username': username})
        user.set_password(password)
        user.is_active = True
        user.save()

        account = Account(**{'name': username, 'internet_nl_api_username': username,
                             'internet_nl_api_password': Account.encrypt_password(password)})
        account.save()

        dashboarduser = DashboardUser(**{'user': user, 'account': account})
        dashboarduser.save()
