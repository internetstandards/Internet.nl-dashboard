# SPDX-License-Identifier: Apache-2.0
# To run these specific tests: tox -e test -- -k test_spreadsheet
from pathlib import Path

from django.contrib.auth.models import User

from dashboard.internet_nl_dashboard.logic.spreadsheet import (get_data, get_upload_history,
                                                               is_file, is_valid_extension,
                                                               is_valid_mimetype,
                                                               log_spreadsheet_upload, save_data)
from dashboard.internet_nl_dashboard.models import Account, DashboardUser

# the 5000 urls has been skipped, it adds nothing to the test cases, only to the load for the UI. Use it for UI
# testing... can the UI really handle thousands of urls efficiently?


path = Path(__file__).parent


def test_spreadsheet(db, redis_server) -> None:
    # Since logs are tied to a user, make sure there is one.
    test_user = User.objects.all().create(username="test")
    test_user.save()

    account, created = Account.objects.all().get_or_create(name="test")

    # establish the relation between user and account:
    dashboarduser, created = DashboardUser.objects.all().get_or_create(notes="test", account=account, user=test_user)

    def test_valid(file):
        valid = is_file(file)
        assert valid is True

        valid = is_valid_extension(file)
        assert valid is True

        valid = is_valid_mimetype(file)
        assert valid is True

        data = get_data(file)
        # should result in two categories
        assert len(data) == 2

        # testsite contains these three
        assert data['testsites'] == {'hdsr.nl', 'zuiderzeeland.nl', 'aaenmaas.nl'}

        # waterschappen should contain 24 items (including two compound items(!))
        assert len(data['waterschappen']) == 24

        saved = save_data(account, data)
        # the test is run multiple times with data, so after the first time, already_in_list is set.
        assert saved['testsites']['added_to_list'] == 3 or saved['testsites']['already_in_list'] == 3

        data = log_spreadsheet_upload(account.dashboarduser_set.first(), file=file, status='test', message="Test")
        assert len(data['original_filename']) > 5

        upload_history = get_upload_history(account)
        assert len(upload_history) > 0

    # Try to work with a malformed CSV file
    file = f'{path}/test spreadsheet uploads/incorrect.csv'
    data = get_data(file)
    assert len(data) == 0

    # Run all tests on a valid file, that complies with the standard etc...
    file = f'{path}/test spreadsheet uploads/waterschappen.ods'
    test_valid(file)

    # should also work for excel files
    file = f'{path}/test spreadsheet uploads/waterschappen.xlsx'
    test_valid(file)

    # We skip this test as it takes long and doesn't really add anything. We could improve it's speed perhaps.
    # It should also work fine with thousands of urls...
    # file = 'tests/test spreadsheet uploads/tenthousand.ods'
    # test_valid(file)

    # Should also be able to handle CSV files, as if they are spreadsheets
    file = f'{path}/test spreadsheet uploads/waterschappen.csv'
    test_valid(file)

    # Now let's see what happens if another octet/stream is uploaded, like an .exe file.
    file = f'{path}/test spreadsheet uploads/tracie/tracie.exe'

    # this will fail because of the file extension
    valid = is_valid_extension(file)
    assert valid is False

    # Let's be evil and rename it to .xlsx, so we bypass both the mime check and the extension check
    # Nope, it finds it's a 'application/x-dosexec'
    file = f'{path}/test spreadsheet uploads/tracie/tracie.xlsx'
    valid = is_valid_mimetype(file)
    assert valid is False

    # Let's instead use a corrupted xlsx that should not work when parsing.
    file = f'{path}/test spreadsheet uploads/waterschappen_corrupted.xlsx'
    valid = is_valid_mimetype(file)
    assert valid is True

    # this will crash and burn, and therefore return an empty set.
    data = get_data(file)
    assert data == {}

    # Mixing datatypes (ints, booleans etc) should just work
    # one of the datatypes is split into two, therefore there are 9 items.
    # The point is to check that importing doesn't crash and some casting to strings work.
    file = f'{path}/test spreadsheet uploads/mixed_datatypes.ods'
    data = get_data(file)
    assert len(data) == 9

    # the original filename can be retrieved (using a heuristic, not exact)
    # the file was already uploaded above, so it should now be renamed internally.
    file = f'{path}/test spreadsheet uploads/waterschappen_WFgL3uS.ods'
    data = log_spreadsheet_upload(dashboarduser, file=file, status='Test', message="Test")
    assert data['original_filename'] == "waterschappen.ods"
    assert data['internal_filename'] != "waterschappen.ods"
