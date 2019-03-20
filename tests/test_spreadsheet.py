# To run these specific tests: tox -e test -- -k test_spreadsheet
from django.contrib.auth.models import User

from dashboard.internet_nl_dashboard.models import Account, DashboardUser
from dashboard.internet_nl_dashboard.spreadsheet import (get_data, get_upload_history, is_file,
                                                         is_valid_extension, is_valid_mimetype,
                                                         log_spreadsheet_upload, save_data,
                                                         validate)

# the 5000 urls has been skipped, it adds nothing to the test cases, only to the load for the UI. Use it for UI
# testing... can the UI really handle thousands of urls efficiently?


def test_spreadsheet(db) -> None:
    # todo: move account and dashboarduser creation to top.

    # Since logs are tied to a user, make sure there is one.
    test_user = User.objects.all().create(username="test")
    test_user.save()

    def test_valid(file):
        valid = is_file(file)
        assert valid is True

        valid = is_valid_extension(file)
        assert valid is True

        valid = is_valid_mimetype(file)
        assert valid is True

        # these are all validations in one.
        valid = validate(file)
        assert valid is True

        data = get_data(file)
        # should result in two categories
        assert len(data) == 2

        # testsite contains these three
        assert data['testsites'] == {'hdsr.nl', 'zuiderzeeland.nl', 'aaenmaas.nl'}

        # waterschappen should contain 24 items (including two compound items(!))
        assert len(data['waterschappen']) == 24

        account, created = Account.objects.all().get_or_create(name="test")
        saved = save_data(account, data)
        # the test is run multiple times with data, so after the first time, already_in_list is set.
        assert saved['testsites']['added_to_list'] == 3 or saved['testsites']['already_in_list'] == 3

        dashboarduser, created = DashboardUser.objects.all().get_or_create(
            notes="test", account=account, user=test_user)

        data = log_spreadsheet_upload(account.dashboarduser_set.first(), file=file, message="Test")
        assert len(data['original_filename']) > 5

        upload_history = get_upload_history(account)
        assert len(upload_history) > 0

    # Run all tests on a valid file, that complies with the standard etc...
    file = 'tests/test spreadsheet uploads/waterschappen.ods'
    test_valid(file)

    # should also work for excel files
    file = 'tests/test spreadsheet uploads/waterschappen.xlsx'
    test_valid(file)

    # It should also work fine with thousands of urls...
    file = 'tests/test spreadsheet uploads/tenthousand.ods'
    test_valid(file)

    # Now let's see what happens if another octet/stream is uploaded, like an .exe file.
    file = 'tests/test spreadsheet uploads/tracie/tracie.exe'

    # this will fail because of the file extension
    valid = validate(file)
    assert valid is False

    # Let's be evil and rename it to .xlsx, so we bypass both the mime check and the extension check
    # Nope, it finds it's a 'application/x-dosexec'
    file = 'tests/test spreadsheet uploads/tracie/tracie.xlxs'
    valid = validate(file)
    assert valid is False

    # Let's instead use a corrupted xlsx that should not work when parsing.
    file = 'tests/test spreadsheet uploads/waterschappen_corrupted.xlsx'
    valid = validate(file)
    assert valid is True

    # this will crash and burn, and therefore return an empty set.
    data = get_data(file)
    assert data == {}

    # Mixing datatypes (ints, booleans etc) should just work
    # one of the datatypes is split into two, therefore there are 9 items.
    # The point is to check that importing doesn't crash and some casting to strings work.
    file = 'tests/test spreadsheet uploads/mixed_datatypes.ods'
    data = get_data(file)
    assert len(data) == 9
