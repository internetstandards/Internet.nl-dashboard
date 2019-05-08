"""
Checks that the password in the Account can be stored and retrieved, and results into the same value.

Run these tests with tox -e test -- -k test_password_storage
"""
import pytest
from django.db import transaction

from dashboard.internet_nl_dashboard.models import Account


def test_password_storage(db, redis_server) -> None:

    # normal usage
    secret_password = 'My voice is my password.'
    account, created = Account.objects.all().get_or_create(name="test")
    account.internet_nl_api_password = account.encrypt_password(secret_password)
    account.save()
    # this does not perform a retrieval, so of course it's the same.
    assert account.decrypt_password() == secret_password

    # no password set, should throw a valueError
    with pytest.raises(ValueError, match=r'.*not set.*'):
        account, created = Account.objects.all().get_or_create(name="value error")
        account.decrypt_password()

    with transaction.atomic():
        # there is no magic going on. Passwords have to be encrypted manually.
        # Warning: the transaction is broken here.
        # An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.
        with pytest.raises(TypeError, match=r'.*bytes-like.*'):
            account.internet_nl_api_password = "bla"
            account.save()

    with pytest.raises(ValueError, match=r'.*not encrypted.*'):
        account.decrypt_password()

    # can create at once:
    account2 = Account()
    account2.name = 'test 2'
    account2.internet_nl_api_username = 'test 2'
    account2.internet_nl_api_password = Account.encrypt_password(secret_password)
    account2.save()

    assert account2.decrypt_password() == secret_password

    # If the field is stored as CharField instead of BinaryField, the type has become a string.
    # It's a bit hard to cast that string back into bytes.
    # verify that when retrieving all accounts, the password fields are still bytes.
    accounts = Account.objects.all().filter(name__in=['test', 'test 2'])

    for account in accounts:
        # assert type(account.internet_nl_api_password) is bytes
        assert account.decrypt_password() == secret_password
