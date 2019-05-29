"""
Run these tests with tox -e test -- -k test_two_factor_integration
"""

# https://docs.djangoproject.com/en/2.1/topics/testing/tools/
from django.test import Client

client = Client()


def test_two_factor_integration(db) -> None:
    """ The first page you visit when logged out should contain something that is used only in the theme.  """
    response = client.get('/', follow=True)
    assert b"Internet Standards Platform" in response.content
