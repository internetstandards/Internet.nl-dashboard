from django.urls import path

from dashboard.internet_nl_dashboard.views import __init__, dashboard, powertools, spreadsheet, urllist

urlpatterns = [
    path('', dashboard.dashboard),
    path('dashboard/', dashboard.dashboard),
    path('powertools/', powertools.powertools),
    path('logout/', __init__.logout_view),

    # todo: the usage of strings as ID's will give problems. Perhaps still call by id... We'll see when it breaks.
    path('addressmanager/', urllist.addressmanager),
    path('data/urllists/get/', urllist.get_lists),
    path('data/urllist/create/', urllist.create_list_),
    path('data/urllist_content/get/<str:urllist_name>/', urllist.get_urllist_content_),
    path('data/urllist/save_list_content/', urllist.save_list_content),

    path('upload/', spreadsheet.upload),
    path('data/upload-spreadsheet/', spreadsheet.upload_spreadsheet),
    path('data/upload-history/', spreadsheet.upload_history)

    # Would you enable the below login form, you will bypass all second factor authentication. Therefore do not enable
    # this url (!)
    # url(r'^login/$', auth_views.LoginView.as_view(template_name='internet_nl_dashboard/registration/login.html'),
    # name='login'),
]
