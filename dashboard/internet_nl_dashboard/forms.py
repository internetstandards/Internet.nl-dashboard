# SPDX-License-Identifier: Apache-2.0
import logging

from django import forms

from dashboard.internet_nl_dashboard.models import Account

log = logging.getLogger(__package__)


class CustomAccountModelForm(forms.ModelForm):
    new_password = forms.CharField(
        help_text='Changing this value will set a new password for this account.',
        required=False
    )

    def save(self, commit=True):
        # new_password = self.cleaned_data.get('new_password', None)
        # self.cleaned_data['internet_nl_api_password'] = Account.encrypt_password(new_password)
        return super().save(commit=commit)

    class Meta:
        model = Account
        fields = '__all__'
