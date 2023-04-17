# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
import redis
from websecmap.conftest import default_policy, default_scan_metadata  # noqa

__all__ = [default_scan_metadata, default_policy]  # prevent code cleaners to automatically remove unused import.


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
