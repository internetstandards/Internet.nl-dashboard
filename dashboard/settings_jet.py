from django.utils.translation import gettext_lazy as _

JET_SIDE_MENU_ITEMS = [

    {'label': '', 'items': [
        {'name': 'constance.config', 'label': '🎛️ Dashboard Configuration'},
        {'name': 'django_mail_admin.emailtemplate', 'label': '📨 E-Mail Templates'},
        {'name': 'django_mail_admin.outbox', 'label': '📨 Outboxes'},
        {'name': 'django_celery_beat.periodictask', 'label': '⏰ Periodic Tasks'},
        {'name': 'auth.user', 'label': '👤 Users'},
        {'name': 'internet_nl_dashboard.account', 'label': '🏢 Accounts'},
        {'name': 'otp_totp.totpdevice', 'label': '📱 TOTP Devices'},
    ]},

    {'label': _('📘 Dashboard'), 'items': [
        {'name': 'internet_nl_dashboard.urllist', 'label': "Domain lists"},
        {'name': 'internet_nl_dashboard.taggedurlinurllist', 'label': 'Tagged Url'},
        {'name': 'internet_nl_dashboard.uploadlog', 'label': 'Uploads'},
    ]},

    {'label': _('🔬 Scan'), 'items': [
        {'name': 'scanners.internetnlscaninspection', 'label': 'Scan Inspections'},
        {'name': 'internet_nl_dashboard.accountinternetnlscan'},
        {'name': 'internet_nl_dashboard.accountinternetnlscanlog'},
        {'name': 'scanners.internetnlv2scan', 'label': 'Internet.nl Scans Tasks'},
        {'name': 'scanners.internetnlv2statelog', 'label': 'Internet.nl Scans Log'},
        {'name': 'internet_nl_dashboard.subdomaindiscoveryscan', 'label': 'Subdomain Discovery'}
    ]},

    {'label': _('💽 Data'), 'items': [
        {'name': 'organizations.url', 'label': 'Urls'},
        {'name': 'scanners.endpoint', 'label': 'Endpoints'},
        {'name': 'scanners.endpointgenericscan', 'label': 'Endpoint Scans'},
    ]},

    {'label': _('📊 Report'), 'items': [
        {'name': 'reporting.urlreport', 'label': 'Url Reports'},
        {'name': 'internet_nl_dashboard.urllistreport', 'label': 'Full Reports'}
    ]},

    {'label': _('🕒 Periodic Tasks'), 'items': [
        {'name': 'django_celery_beat.periodictask'},
        {'name': 'django_celery_beat.crontabschedule'},
    ]},

    {'label': _('📨 E-Mail'), 'items': [
        {'name': 'django_mail_admin.emailtemplate', 'label': 'Templates'},
        {'name': 'django_mail_admin.outgoingemail', 'label': 'Sent mail'},
        {'name': 'django_mail_admin.outbox', 'label': 'Outboxes'},
        {'name': 'django_mail_admin.log', 'label': 'Logs'},
    ]},

    {'label': _('✨ Activity'), 'items': [
        {'name': 'actstream.action'},
    ]},
]

JET_SIDE_MENU_COMPACT = True
