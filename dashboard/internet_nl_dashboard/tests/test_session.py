from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.http import HttpRequest, QueryDict
from dashboard.internet_nl_dashboard.views.session import session_login_
import logging

log = logging.getLogger(__package__)


def test_session(db):

    user = User()
    user.username = "test"
    user.set_password('test')
    user.is_active = True
    user.save()

    # correct login:
    newrequest = HttpRequest()
    newrequest.method = 'POST'
    newrequest.session = SessionStore("")
    newrequest.POST = QueryDict(query_string="{'username':'test','password':'test'}")
    response = session_login_(newrequest)
    log.debug(response)
    assert response['success'] is True

    # wrong login
    newrequest = HttpRequest()
    newrequest.method = 'POST'
    newrequest.session = SessionStore("")
    newrequest.POST = QueryDict(query_string='username=test&password=false_password')
    response = session_login_(newrequest)
    log.debug(response)
    assert response['success'] is False

