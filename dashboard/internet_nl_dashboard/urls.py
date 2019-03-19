from django.urls import path

from dashboard.internet_nl_dashboard import views

urlpatterns = [
    path('', views.index),
    path('dashboard/', views.dashboard),
    path('addressmanager/', views.addressmanager),
    path('logout/', views.logout_view),

    # Would you enable the below login form, you will bypass all second factor authentication. Therefore do not enable
    # this url (!)
    # url(r'^login/$', auth_views.LoginView.as_view(template_name='internet_nl_dashboard/registration/login.html'),
    # name='login'),

    path('data/urllists/get/', views.get_lists),
    path('data/urllist/create/', views.create_list_),
    path('data/urllist_content/get/', views.get_urllist_content),
    path('data/urllist/save_list_content/', views.save_list_content)

]
