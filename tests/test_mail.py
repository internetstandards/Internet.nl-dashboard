# SPDX-License-Identifier: Apache-2.0
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from django_mail_admin.models import EmailTemplate, Log, Outbox, OutgoingEmail, TemplateVariable
from websecmap.scanners.models import InternetNLV2Scan

from dashboard.internet_nl_dashboard.logic.mail import (email_configration_is_correct,
                                                        generate_unsubscribe_code,
                                                        get_users_to_send_mail_to,
                                                        send_scan_finished_mails, unsubscribe)
from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan, DashboardUser,
                                                    UrlList, UrlListReport)


def setup_test():
    user = User(**{'first_name': 'test', 'last_name': 'test', 'username': 'test', 'is_active': True})
    user.save()

    account = Account(**{'name': 'test'})
    account.save()

    dashboarduser = DashboardUser(**{'mail_preferred_mail_address': 'info@example.com', 'mail_preferred_language': 'nl',
                                     'mail_send_mail_after_scan_finished': True, 'account': account, 'user': user})
    dashboarduser.save()

    urllist = UrlList(**{'name': '', 'account': account})
    urllist.save()

    urllistreport = UrlListReport(**{'urllist': urllist, 'average_internet_nl_score': 42.42, 'at_when': timezone.now()})
    urllistreport.save()

    internetnlv2scan = InternetNLV2Scan(**{'type': 'web', 'scan_id': '123', 'state': 'finished'})
    internetnlv2scan.save()

    accountinternetnlscan = AccountInternetNLScan(
        **{'account': account, 'scan': internetnlv2scan, 'urllist': urllist, 'started_on': timezone.now(),
           'report': urllistreport, 'finished_on': timezone.now() + timedelta(hours=2)})
    accountinternetnlscan.save()

    # first template:
    template = EmailTemplate()
    template.name = "scan_finished_en"
    template.subject = "test"
    template.description = "test"
    template.email_html_text = "test {{report_average_internet_nl_score}}."
    template.save()


def test_send_scan_finished_mails(db) -> None:
    setup_test()

    accountinternetnlscan = AccountInternetNLScan.objects.first()
    send_scan_finished_mails(accountinternetnlscan)

    # we should now have a mail in the outbox and something in the logs
    sent_mail = OutgoingEmail.objects.all().first()

    # default address
    assert sent_mail.from_email == "noreply@dashboard.internet.nl"
    assert sent_mail.to == ["info@example.com"]
    assert sent_mail.template == EmailTemplate.objects.get(name="scan_finished_en")

    # values are saved as TemplateVariable
    templatevariable = TemplateVariable.objects.all().filter(name='report_average_internet_nl_score').first()
    assert templatevariable.name == "report_average_internet_nl_score"
    assert templatevariable.value == "42.42"
    assert templatevariable.email == sent_mail

    # user now has an unsubscribe code:
    dbu = DashboardUser.objects.all().first()
    assert dbu.mail_send_mail_after_scan_finished is True
    assert len(dbu.mail_after_mail_unsubscribe_code) == 128

    # fail a unsubscription
    unsubscribe('scan_finished', "fake code!")
    dbu = DashboardUser.objects.all().first()
    assert dbu.mail_send_mail_after_scan_finished is True
    assert len(dbu.mail_after_mail_unsubscribe_code) == 128

    # unsubscribe from the feed
    unsubscribe('scan_finished', dbu.mail_after_mail_unsubscribe_code)
    dbu = DashboardUser.objects.all().first()
    assert len(dbu.mail_after_mail_unsubscribe_code) == 0
    assert dbu.mail_send_mail_after_scan_finished is False

    # log is empty
    assert Log.objects.all().first() is None


def test_generate_unsubscribe_code():
    assert len(generate_unsubscribe_code()) == 128


def test_get_users_to_send_mail_to(db):
    setup_test()
    # validate that null and empty is not used.
    accountinternetnlscan = AccountInternetNLScan.objects.first()

    assert len(get_users_to_send_mail_to(accountinternetnlscan)) == 1

    # send no mail when there is no mail address, it's empty, not null
    dbu = DashboardUser.objects.all().first()
    dbu.mail_preferred_mail_address = ""
    dbu.save()
    assert len(get_users_to_send_mail_to(accountinternetnlscan)) == 0

    # send no mail when there is no mail address, it's null
    dbu = DashboardUser.objects.all().first()
    dbu.mail_preferred_mail_address = None
    dbu.save()
    assert len(get_users_to_send_mail_to(accountinternetnlscan)) == 0

    # will not send a mail if mail_send_mail_after_scan_finished is false
    dbu = DashboardUser.objects.all().first()
    dbu.mail_preferred_mail_address = "info@example.com"
    dbu.mail_send_mail_after_scan_finished = False
    dbu.save()
    assert len(get_users_to_send_mail_to(accountinternetnlscan)) == 0

    # will not send if is_active is false:
    dbu = DashboardUser.objects.all().first()
    dbu.mail_send_mail_after_scan_finished = True
    usr = User.objects.all().filter(dashboarduser=dbu).first()
    usr.is_active = False
    usr.save()
    dbu.save()
    assert len(get_users_to_send_mail_to(accountinternetnlscan)) == 0

    # revert everything and we'll be able to send things again
    dbu = DashboardUser.objects.all().first()
    usr = User.objects.all().filter(dashboarduser=dbu).first()
    usr.is_active = True
    usr.save()
    assert len(get_users_to_send_mail_to(accountinternetnlscan)) == 1


def test_email_configration_is_correct(db):
    """
    Having an outbox is correct. We don't know what outbox is used, nor do we know what settings will be used.

    :param db:
    :return:
    """

    assert email_configration_is_correct() is False

    outbox = Outbox()
    outbox.save()

    assert email_configration_is_correct() is True


def test_urllistreport_get_previous_report(db):
    account = Account(**{'name': 'test'})
    account.save()

    u = UrlList(**{'name': '', 'account': account})
    u.save()

    urllistreport1 = UrlListReport(**{'urllist': u, 'average_internet_nl_score': 1, 'at_when': datetime(2020, 5, 1)})
    urllistreport1.save()

    urllistreport2 = UrlListReport(**{'urllist': u, 'average_internet_nl_score': 1, 'at_when': datetime(2020, 5, 2)})
    urllistreport2.save()

    urllistreport3 = UrlListReport(**{'urllist': u, 'average_internet_nl_score': 1, 'at_when': datetime(2020, 5, 3)})
    urllistreport3.save()

    urllistreport4 = UrlListReport(**{'urllist': u, 'average_internet_nl_score': 1, 'at_when': datetime(2020, 5, 4)})
    urllistreport4.save()

    urllistreport5 = UrlListReport(**{'urllist': u, 'average_internet_nl_score': 1, 'at_when': datetime(2020, 5, 5)})
    urllistreport5.save()

    assert urllistreport5.get_previous_report_from_this_list() == urllistreport4
    assert urllistreport4.get_previous_report_from_this_list() == urllistreport3
    assert urllistreport3.get_previous_report_from_this_list() == urllistreport2
    assert urllistreport2.get_previous_report_from_this_list() == urllistreport1
    assert urllistreport1.get_previous_report_from_this_list() is None
