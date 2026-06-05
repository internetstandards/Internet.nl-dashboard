# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
import redis
from django.apps import apps
from websecmap.reporting.time_cache import CACHE
from websecmap.scanners_common.tests import enable_scanners


@pytest.fixture
def default_scan_metadata(db):
    apps.get_app_config("scanners_internet_nl_web").startup()
    apps.get_app_config("scanners_internet_nl_mail").startup()
    scanners = enable_scanners(["internet_nl_web", "internet_nl_mail"])
    for scanner in scanners.values():
        scanner.creates_scan_types.update(include_in_report=True, show_in_frontend=True)
    CACHE.pop("backend_scanmetadata", None)
    return scanners

@pytest.fixture
def redis_server():
    r = redis.Redis()
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        pytest.skip("redis server not running")


@pytest.fixture
def current_path():
    path = Path(__file__).parent
    yield path
