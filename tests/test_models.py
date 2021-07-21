from datetime import datetime, timedelta

import pytest
import pytz
from django.utils import timezone
from freezegun import freeze_time

from dashboard.internet_nl_dashboard.models import determine_next_scan_moment


def test_determine_next_scan_moment():

    preference = 'every half year'
    tests = [
        {"input": "2012-01-01", "outcome": datetime(year=2012, month=7, day=1, tzinfo=pytz.utc)},
        {"input": "2012-06-30", "outcome": datetime(year=2012, month=7, day=1, tzinfo=pytz.utc)},
        {"input": "2012-07-01", "outcome": datetime(year=2013, month=1, day=1, tzinfo=pytz.utc)},
        {"input": "2012-12-31", "outcome": datetime(year=2013, month=1, day=1, tzinfo=pytz.utc)},
        {"input": "2012-03-04", "outcome": datetime(year=2012, month=7, day=1, tzinfo=pytz.utc)},
    ]

    for test in tests:
        with freeze_time(test["input"]):
            assert test["outcome"] == determine_next_scan_moment(preference)

    preference = "at the start of every quarter"
    tests = [
        {"input": "2012-01-14", "outcome": datetime(year=2012, month=4, day=1, tzinfo=pytz.utc)},
        {"input": "2012-04-16", "outcome": datetime(year=2012, month=7, day=1, tzinfo=pytz.utc)},
        {"input": "2012-06-14", "outcome": datetime(year=2012, month=7, day=1, tzinfo=pytz.utc)},
        {"input": "2012-07-14", "outcome": datetime(year=2012, month=10, day=1, tzinfo=pytz.utc)},
        {"input": "2012-12-31", "outcome": datetime(year=2013, month=1, day=1, tzinfo=pytz.utc)},
    ]

    for test in tests:
        with freeze_time(test["input"]):
            assert test["outcome"] == determine_next_scan_moment(preference)

    preference = "every 1st day of the month"
    tests = [
        {"input": "2012-01-01", "outcome": datetime(year=2012, month=2, day=1, tzinfo=pytz.utc)},
        {"input": "2012-01-31", "outcome": datetime(year=2012, month=2, day=1, tzinfo=pytz.utc)},
        {"input": "2012-02-01", "outcome": datetime(year=2012, month=3, day=1, tzinfo=pytz.utc)},
        {"input": "2012-12-31", "outcome": datetime(year=2013, month=1, day=1, tzinfo=pytz.utc)},
        {"input": "2012-06-16", "outcome": datetime(year=2012, month=7, day=1, tzinfo=pytz.utc)},
    ]

    for test in tests:
        with freeze_time(test["input"]):
            assert test["outcome"] == determine_next_scan_moment(preference)

    preference = "twice per month"
    tests = [
        {"input": "2012-01-01", "outcome": datetime(year=2012, month=1, day=15, tzinfo=pytz.utc)},
        {"input": "2012-01-31", "outcome": datetime(year=2012, month=2, day=1, tzinfo=pytz.utc)},
        {"input": "2012-02-01", "outcome": datetime(year=2012, month=2, day=15, tzinfo=pytz.utc)},
        {"input": "2012-12-04", "outcome": datetime(year=2012, month=12, day=15, tzinfo=pytz.utc)},
        {"input": "2012-12-31", "outcome": datetime(year=2013, month=1, day=1, tzinfo=pytz.utc)},
        {"input": "2012-06-14", "outcome": datetime(year=2012, month=6, day=15, tzinfo=pytz.utc)},
        {"input": "2012-06-15", "outcome": datetime(year=2012, month=7, day=1, tzinfo=pytz.utc)},
    ]

    for test in tests:
        with freeze_time(test["input"]):
            assert test["outcome"] == determine_next_scan_moment(preference)

    preference = "disabled"
    # dates, because there will be a difference in milliseconds as timezone.now is executed at different moments.
    # date comparing will fail when the exact moment is 00:00:00 because the date is different. Therefore the < is used.
    assert (timezone.now() + timedelta(days=9000)) <= determine_next_scan_moment(preference)

    with pytest.raises(ValueError):
        determine_next_scan_moment("NONSENSE")
