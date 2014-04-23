from flexmock import flexmock
from mfcloud import txhttp
from mfcloud.test_utils import real_docker, mock_docker
from mfcloud.txdocker import DockerTwistedClient, DockerConnectionFailed
import pytest
from twisted.internet import defer


@pytest.fixture
def client():
    with mock_docker():
        client = DockerTwistedClient()
        return client


@pytest.inlineCallbacks
def test_request(client):
    """
    @type client: DockerTwistedClient
    """

    def test(url, **kwargs):
        assert url == 'unix://var/run/docker.sock//boooooo'

        assert 'data' in kwargs
        assert kwargs['data'] == {'foo': 'bar'}
        assert 'headers' in kwargs
        assert kwargs['headers'] == {'x': 'boo'}

        return defer.succeed('foobar')

    result = yield client._request('boooooo', data={'foo': 'bar'}, response_handler=None, headers={'x': 'boo'}, method=test)

    assert result == 'foobar'

@pytest.inlineCallbacks
def test_wrong_url_connection_refused():

    client = DockerTwistedClient(timeout=1)
    client.url = 'http://ci.dev.modera.org:1'

    with pytest.raises(DockerConnectionFailed):
        yield client._get('foo')


@pytest.inlineCallbacks
def test_wrong_url_wrong_port():

    client = DockerTwistedClient(timeout=2)
    client.url = 'http://ci.dev.modera.org:22'

    with pytest.raises(DockerConnectionFailed):
        yield client._get('foo')


def test_get(client):

    flexmock(client)
    client.should_receive('_request').with_args(url='foo?foo=bar&boo=1',  method=txhttp.get, foo='bar').once().and_return('baz')

    assert client._get('foo', foo='bar', data={'foo': 'bar', 'boo': 1}) == 'baz'


def test_post(client):

    flexmock(client)
    client.should_receive('_request').with_args(url='foo', method=txhttp.post, foo='bar').once().and_return('baz')

    assert client._post('foo', foo='bar') == 'baz'


def test_delete(client):

    flexmock(client)
    client.should_receive('_request').with_args(url='foo', method=txhttp.delete, foo='bar').once().and_return('baz')

    assert client._delete('foo', foo='bar') == 'baz'

