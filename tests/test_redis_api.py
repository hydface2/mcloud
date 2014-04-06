import pytest


import txredisapi as redis

@pytest.inlineCallbacks
def test_incr():
    rc = yield redis.Connection()

    yield rc.set("foo", 4)

    v = yield rc.get("foo")

    assert v == 4

    v = yield rc.incr("foo")

    assert v == 5

    yield rc.disconnect()