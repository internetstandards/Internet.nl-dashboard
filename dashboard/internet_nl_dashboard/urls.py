# SPDX-License-Identifier: Apache-2.0
from constance import config
from django.shortcuts import redirect
from django.urls import path, register_converter
from websecmap.map.views import security_txt

# We have to import the signals somewhere..?!
import dashboard.internet_nl_dashboard.signals  # noqa  # pylint: disable=unused-import
from dashboard.internet_nl_dashboard.views import (account, domains, download_spreadsheet, logout_view, mail,
                                                   powertools, report, scan_monitor, session, signup, spreadsheet,
                                                   subdomains, tags, usage, user)


class SpreadsheetFileTypeConverter:
    # Supports {"key": "value", "key2": "value2"} syntax.
    regex = '(xlsx|ods|csv)'

    @staticmethod
    def to_python(value):
        return str(value)

    @staticmethod
    def to_url(value):
        return f'{value}'


register_converter(SpreadsheetFileTypeConverter, 'spreadsheet_filetype')


urlpatterns = [
    path('', lambda request: redirect(config.DASHBOARD_FRONTEND_URL)),
    # The SPA is not reachable anymore.
    # path('spa/', powertools.spa),
    path('data/powertools/get_accounts/', powertools.get_accounts),
    path('data/powertools/set_account/', powertools.set_account),
    path('data/powertools/save_instant_account/', powertools.save_instant_account),
    path('logout/', logout_view),

    # domain management
    path('data/urllists/get/', domains.get_lists),
    path('data/urllist_content/get/<int:urllist_id>/', domains.get_urllist_content_),
    path('data/urllist/save_list_content/', domains.save_list_content),
    path('data/urllist/update_list_settings/', domains.update_list_settings_),
    path('data/urllist/get_scan_status_of_list/<int:urllist_id>/', domains.get_scan_status_of_list_),
    path('data/urllist/create_list/', domains.create_list_),
    path('data/urllist/delete/', domains.delete_list_),
    path('data/urllist/scan_now/', domains.scan_now_),
    path('data/urllist/discover-subdomains/<int:urllist_id>/', subdomains.request_subdomain_discovery_scan_),
    path('data/urllist/discover-subdomains-status/<int:urllist_id>/', subdomains.subdomain_discovery_scan_status_),
    path('data/urllist/url/save/', domains.alter_url_in_urllist_),
    path('data/urllist/url/add/', domains.add_urls_to_urllist),
    path('data/urllist/url/delete/', domains.delete_url_from_urllist_),
    path('data/urllist/download/', domains.download_list_),
    path('data/urllist/upload/<int:list_id>/', spreadsheet.upload_list_),

    path('data/urllist/tag/add/', tags.add_tag_),
    path('data/urllist/tag/remove/', tags.remove_tag_),
    path('data/urllist/tag/list/<int:urllist_id>/', tags.tags_in_urllist_),

    # account management:
    path('data/account/report_settings/get/', account.get_report_settings_),
    path('data/account/report_settings/save/', account.save_report_settings_),

    path('data/user/get/', user.get_user_settings_),
    path('data/user/save/', user.save_user_settings_),

    # uploads of domains
    path('upload/', spreadsheet.upload),
    path('data/upload-spreadsheet/', spreadsheet.upload_spreadsheet),
    path('data/upload-history/', spreadsheet.upload_history),

    # scans / scan monitor
    path('data/scan-monitor/', scan_monitor.running_scans),
    path('data/scan/cancel/', domains.cancel_scan_),

    path('data/report/get/<int:report_id>/', report.get_report_),
    path('data/report/shared/<str:report_code>/', report.get_shared_report_),
    path('data/report/public/', report.get_public_reports_),

    path('data/report/ad_hoc/<int:report_id>/', report.get_ad_hoc_tagged_report_),
    path('data/report/ad_hoc_save/<int:report_id>/', report.save_ad_hoc_tagged_report_),

    path('data/report/share/share/', report.x_share),
    path('data/report/share/unshare/', report.x_unshare),
    path('data/report/share/update_share_code/', report.x_update_share_code),
    path('data/report/share/update_report_code/', report.x_update_report_code),

    path('data/report/public/account/<int:account_id>/lists/all/', report.get_publicly_shared_lists_per_account_),
    path('data/report/public/account/<int:account_id>/lists/<int:urllist_id>/',
         report.get_publicly_shared_lists_per_account_and_list_id_),
    path('data/report/public/lists/<int:urllist_id>/latest/',
         report.get_latest_report_id_from_list),
    path('data/report/public/lists/<int:urllist_id>/latest/<str:report_type>/',
         report.get_latest_report_id_from_list_and_type_),


    path('data/report/differences_compared_to_current_list/<int:report_id>/',
         report.get_report_differences_compared_to_current_list_),
    path('data/report/get_previous/<int:urllist_id>/<str:at_when>/', report.get_previous_report_),

    path('data/report/recent/', report.get_recent_reports_),
    path('data/report/urllist_timeline_graph/<str:urllist_ids>/<str:report_type>/',
         report.get_urllist_report_graph_data_),
    path('data/download-spreadsheet/<int:report_id>/<spreadsheet_filetype:file_type>/',
         download_spreadsheet.download_spreadsheet),

    path('data/usage/', usage.usage_),

    path('mail/unsubscribe/<str:feed>/<str:unsubscribe_code>/', mail.unsubscribe_),

    path('data/signup/', signup.process_application),

    # session management
    # logging in via javascript is not possible, because the CSRF is tied to the session cookie.
    # The session cookie cannot be requested by javascript, and we're not going to use JWT because
    # the second factor part is also django only, and not implmented as REST methods.
    # So there is currently no way to move to rest based auth _including_ second factor authentication.
    # of course except OAUTH, but there is no knowledge for that yet.
    path('session/login/', session.session_login),
    path('session/logout/', session.session_logout),
    path('session/status/', session.session_status),
    # Would you enable the below login form, you will bypass all second factor authentication. Therefore do not enable
    # this url (!)
    # url(r'^login/$', auth_views.LoginView.as_view(template_name='internet_nl_dashboard/registration/login.html'),
    # name='login'),

    path("security.txt", security_txt, name="security_txt"),
    path(".well-known/security.txt", security_txt, name="well_known_security_txt"),
]
