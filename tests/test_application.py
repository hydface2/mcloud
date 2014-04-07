from flexmock import flexmock
from mfcloud.application import Application, ApplicationController
from mfcloud.config import YamlConfig
from mfcloud.container import DockerfileImageBuilder
from mfcloud.service import Service
from mfcloud.util import inject_services
import os
import pytest
import txredisapi


def test_new_app_instance():

    app = Application({'path': 'foo/bar'})
    assert app.config['path'] == 'foo/bar'

def test_app_load():

    app = Application({'path': os.path.realpath(os.path.dirname(__file__) + '/../')})
    config = app.load()

    assert isinstance(config, YamlConfig)
    assert len(config.get_services()) == 1

    assert isinstance(config.get_services()['controller'], Service)
    assert isinstance(config.get_services()['controller'].image_builder, DockerfileImageBuilder)


@pytest.inlineCallbacks
def test_app_controller():

    redis = yield txredisapi.Connection(dbid=2)
    yield redis.flushdb()

    def configure(binder):
        binder.bind(txredisapi.Connection, redis)

    with inject_services(configure):
        controller = ApplicationController()

        r = yield controller.get('foo')
        assert r is None

        r = yield controller.create('foo', 'some/path')
        assert isinstance(r, Application)
        assert r.config['path'] == 'some/path'

        r = yield controller.get('foo')
        assert isinstance(r, Application)
        assert r.config['path'] == 'some/path'

        r = yield controller.create('boo', 'other/path')
        assert isinstance(r, Application)
        assert r.config['path'] == 'other/path'

        r = yield controller.list()

        assert isinstance(r, dict)
        assert len(r) == 2
        for app in r.values():
            assert isinstance(app, Application)

        yield controller.remove('foo')

        r = yield controller.get('foo')
        assert r is None

