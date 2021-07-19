from django.contrib.auth.models import User
from django_countries.fields import Country

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.logic.user import get_user_settings, save_user_settings
from dashboard.internet_nl_dashboard.models import Account, DashboardUser


def test_user_editing(db):

    user = User()
    user.first_name = "test"
    user.last_name = "test"
    user.save()

    account = Account()
    account.name = "test account"
    account.save()

    dashboarduser = DashboardUser()
    dashboarduser.user = user
    dashboarduser.account = account
    dashboarduser.mail_send_mail_after_scan_finished = True
    dashboarduser.mail_preferred_language = 'en'
    dashboarduser.mail_preferred_mail_address = 'info@example.com'
    dashboarduser.save()

    data = get_user_settings(1)

    assert data == {
        'first_name': 'test',
        'last_name': 'test',
        'date_joined': None,
        'last_login': None,
        'account_id': 1,
        'account_name': "test account",
        'mail_preferred_mail_address': "info@example.com",
        'mail_preferred_language': Country(code='en'),
        'mail_send_mail_after_scan_finished': True
    }

    # make a correct change on all fields that we can change.
    new_data = {
        'first_name': 'example',
        'last_name': 'example',
        'mail_preferred_mail_address': 'example@example.com',
        'mail_preferred_language': 'nl',
        'mail_send_mail_after_scan_finished': False
    }
    response = save_user_settings(1, new_data)
    del (response['timestamp'])

    expected_response = operation_response(success=True, message="save_user_settings_success")
    del (expected_response['timestamp'])

    assert response == expected_response

    user = User.objects.all().first()
    assert user.first_name == "example"
    assert user.last_name == "example"
    assert user.dashboarduser.mail_preferred_mail_address == "example@example.com"
    assert user.dashboarduser.mail_preferred_language == Country(code='nl')
    assert user.dashboarduser.mail_send_mail_after_scan_finished is False

    # todo: make all error situations happen.
