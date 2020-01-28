from django.shortcuts import redirect
from django.urls import path, register_converter

# We have to import the signals somewhere..?!
import dashboard.internet_nl_dashboard.signals  # noqa
from dashboard.internet_nl_dashboard.views import (__init__, account, domains, download_spreadsheet,
                                                   powertools, report, scan_monitor, spreadsheet)


class SpreadsheetFileTypeConverter:
    # Supports {"key": "value", "key2": "value2"} syntax.
    regex = '(xlsx|ods|csv)'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return '%s' % value


register_converter(SpreadsheetFileTypeConverter, 'spreadsheet_filetype')


urlpatterns = [
    path('', lambda request: redirect('/spa/#/domains')),
    path('spa/', powertools.spa),
    path('data/powertools/get_accounts/', powertools.get_accounts),
    path('data/powertools/set_account/', powertools.set_account),
    path('data/powertools/save_instant_account/', powertools.save_instant_account),
    path('logout/', __init__.logout_view),

    # domain management
    path('data/urllists/get/', domains.get_lists),
    path('data/urllist_content/get/<int:urllist_id>/', domains.get_urllist_content_),
    path('data/urllist/save_list_content/', domains.save_list_content),
    path('data/urllist/update_list_settings/', domains.update_list_settings_),
    path('data/urllist/get_scan_status_of_list/<int:urllist_id>/', domains.get_scan_status_of_list_),
    path('data/urllist/create_list/', domains.create_list_),
    path('data/urllist/delete/', domains.delete_list_),
    path('data/urllist/scan_now/', domains.scan_now_),
    path('data/urllist/url/save/', domains.alter_url_in_urllist_),
    path('data/urllist/url/add/', domains.add_urls_to_urllist),
    path('data/urllist/url/delete/', domains.delete_url_from_urllist_),

    # account management:
    path('data/account/report_settings/get/', account.get_report_settings_),
    path('data/account/report_settings/save/', account.save_report_settings_),

    # uploads of domains
    path('upload/', spreadsheet.upload),
    path('data/upload-spreadsheet/', spreadsheet.upload_spreadsheet),
    path('data/upload-history/', spreadsheet.upload_history),

    # scans / scan monitor
    path('data/scan-monitor/', scan_monitor.running_scans),
    path('data/scan/cancel/', domains.cancel_scan_),

    path('data/report/get/<int:report_id>/', report.get_report_),
    path('data/report/differences_compared_to_current_list/<int:report_id>/',
         report.get_report_differences_compared_to_current_list_),
    path('data/report/get_previous/<int:urllist_id>/<str:at_when>/', report.get_previous_report_),

    path('data/report/recent/', report.get_recent_reports_),
    path('data/report/urllist_timeline_graph/<str:urllist_ids>/', report.get_urllist_report_graph_data_),
    path('data/download-spreadsheet/<int:report_id>/<spreadsheet_filetype:file_type>/',
         download_spreadsheet.download_spreadsheet)

    # Would you enable the below login form, you will bypass all second factor authentication. Therefore do not enable
    # this url (!)
    # url(r'^login/$', auth_views.LoginView.as_view(template_name='internet_nl_dashboard/registration/login.html'),
    # name='login'),
]
