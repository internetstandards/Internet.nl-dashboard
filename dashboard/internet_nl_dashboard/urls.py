from django.urls import path, register_converter

from dashboard.internet_nl_dashboard.views import (__init__, dashboard, download_spreadsheet,
                                                   powertools, scan_monitor, spreadsheet, urllist)


class SpreadsheetFileTypeConverter:
    # Supports {"key": "value", "key2": "value2"} syntax.
    regex = '(xlsx|ods|csv)'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return '%s' % value


register_converter(SpreadsheetFileTypeConverter, 'spreadsheet_filetype')


urlpatterns = [
    path('', dashboard.dashboard),
    path('powertools/', powertools.powertools),
    path('logout/', __init__.logout_view),

    # todo: the usage of strings as ID's will give problems. Perhaps still call by id... We'll see when it breaks.
    path('addressmanager/', urllist.addressmanager),
    path('data/urllists/get/', urllist.get_lists),
    path('data/urllist/create/', urllist.create_list_),
    path('data/urllist_content/get/<str:urllist_id>/', urllist.get_urllist_content_),
    path('data/urllist/save_list_content/', urllist.save_list_content),

    path('upload/', spreadsheet.upload),
    path('data/upload-spreadsheet/', spreadsheet.upload_spreadsheet),
    path('data/upload-history/', spreadsheet.upload_history),

    path('scan-monitor/', scan_monitor.scan_monitor),
    path('data/scan-monitor/', scan_monitor.running_scans),

    # reporting
    path('dashboard/', dashboard.dashboard),
    path('data/report/get/<int:report_id>/', dashboard.get_report_),
    path('data/report/recent/', dashboard.get_recent_reports_),
    path('data/download-spreadsheet/<int:report_id>/<spreadsheet_filetype:file_type>/',
         download_spreadsheet.download_spreadsheet)

    # Would you enable the below login form, you will bypass all second factor authentication. Therefore do not enable
    # this url (!)
    # url(r'^login/$', auth_views.LoginView.as_view(template_name='internet_nl_dashboard/registration/login.html'),
    # name='login'),
]
