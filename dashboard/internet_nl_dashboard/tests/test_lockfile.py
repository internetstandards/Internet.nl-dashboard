# SPDX-License-Identifier: Apache-2.0
from time import sleep

from freezegun import freeze_time

from dashboard.lockfile import lock_expired, remove_lock, temporary_file_lock


def test_lockfile(mocker):

    # Reset environment
    remove_lock('test1')

    # 2020-01-01 == 1577836800
    mocker.patch("os.path.getmtime", return_value=1577836800)

    with freeze_time("2020-01-01") as frozen_datetime:

        # Cannot open the same lock when it's open:
        if temporary_file_lock('test1'):
            sleep(1)
            assert temporary_file_lock('test1') is False

        # Remove it and then claim it:
        remove_lock('test1')
        assert temporary_file_lock('test1') is True

        # Can't claim it again, unless we're far in the future
        assert temporary_file_lock('test1') is False
        assert lock_expired('test1', 300) is False

        # Now go into the future and see that it can be claimed
        frozen_datetime.move_to("2020-01-02")
        assert lock_expired('test1', 300) is True
        assert temporary_file_lock('test1') is True

        mocker.patch("os.path.getmtime", return_value=1577923200)
        assert lock_expired('test1', 300) is False
        assert temporary_file_lock('test1') is False
        assert temporary_file_lock('test1') is False
