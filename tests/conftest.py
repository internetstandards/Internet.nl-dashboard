import pytest
import redis


@pytest.fixture
def redis_server():
    r = redis.Redis()
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        pytest.skip("redis server not running")
