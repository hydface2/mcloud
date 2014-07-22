import json
import logging
import sys


from autobahn.wamp import router
from autobahn.twisted.util import sleep
from autobahn.twisted import wamp, websocket


import inject
from mfcloud.dns_resolver import listen_dns, dump_resolv_conf
from mfcloud.events import EventBus
from mfcloud.plugins.dns import DnsPlugin
from mfcloud.plugins.haproxy import HaproxyPlugin
from mfcloud.plugins.monitor import DockerMonitorPlugin
from mfcloud.tasks import TaskService
from mfcloud.txdocker import IDockerClient, DockerTwistedClient
from mfcloud.util import txtimeout
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import serverFromString
from twisted.web import xmlrpc, server
import txredisapi
from txzmq import ZmqFactory, ZmqEndpoint, ZmqPubConnection



class ApiRpcServer(object):

    redis = inject.attr(txredisapi.Connection)
    eb = inject.attr(EventBus)

    def __init__(self):
        self.tasks = {}
        self.ticket_map = {}

    def task_completed(self, result, ticket_id):
        self.ticket_map[ticket_id].sendMessage(json.dumps())

    def task_failed(self, error, ticket_id):
        print 'Failure: <%s> %s' % (error.type, error.getErrorMessage())
        print error.printTraceback()

        self.eb.fire_event('task.failed.%s' % ticket_id, "Failed: <%s> %s" % (error.type, error.getErrorMessage()))

    @inlineCallbacks
    def task_start(self, client, task_name, *args, **kwargs):
        """
        Return all passed args.
        """

        ticket_id = yield self.redis.incr('mfcloud-ticket-id')

        self.ticket_map[ticket_id] = client

        if not task_name in self.tasks:
            raise ValueError('No such task: %s' % task_name)
        task_defered = self.tasks[task_name](ticket_id, *args, **kwargs)

        task_defered.addCallback(self.task_completed, ticket_id)
        task_defered.addErrback(self.task_failed, ticket_id)

        defer.returnValue(ticket_id)


    def xmlrpc_is_completed(self, ticket_id):
        d = self.redis.get('mfcloud-ticket-%s-completed' % ticket_id)

        def on_result(result):
            return result == 1

        d.addCallback(on_result)
        return d

    def xmlrpc_get_result(self, ticket_id):
        d = self.redis.get('mfcloud-ticket-%s-result' % ticket_id)
        d.addCallback(lambda result: json.loads(result))
        return d


def entry_point():

    console_handler = logging.StreamHandler(stream=sys.stderr)
    console_handler.setFormatter(logging.Formatter(fmt='[%(asctime)s][%(levelname)s][%(name)s] %(message)s'))
    console_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)
    root_logger.debug('Logger initialized')

    import argparse

    parser = argparse.ArgumentParser(description='Dns resolver')

    parser.add_argument('--port', type=int, default=7080, help='port number')
    parser.add_argument('--haproxy', default=False, action='store_true', help='Update haproxy config')
    # parser.add_argument('--dns', type=bool, default=True, action='store_true', help='Start dns server')
    # parser.add_argument('--events', type=bool, default=True, action='store_true', help='Start dns server')
    parser.add_argument('--dns-server-ip', type=str, default='172.17.42.1', help='Dns server to use in containers')
    parser.add_argument('--dns-search-suffix', type=str, default='mfcloud.lh', help='Dns suffix to use')
    parser.add_argument('--host-ip', type=str, default=None, help='Proxy destination for non-local traffic')
    parser.add_argument('--interface', type=str, default='0.0.0.0', help='ip address')
    parser.add_argument('--zmq-bind', type=str, default='tcp://0.0.0.0:5555', help='ip address')

    args = parser.parse_args()

    rpc_interface = args.interface
    rpc_port = args.port
    dns_server_ip = args.dns_server_ip
    dns_prefix = args.dns_search_suffix

    def listen_rpc():
        from twisted.python import log
        log.startLogging(sys.stdout)
        print '1'
        router_factory = router.RouterFactory()
        print '2'
        session_factory = wamp.RouterSessionFactory(router_factory)
        print '3'
        session_factory.add(TaskService())
        print '4'
        transport_factory = websocket.WampWebSocketServerFactory(session_factory)
        print '5'

        server = serverFromString(reactor, "tcp:7080")
        print '6'
        server.listen(transport_factory)
        print '7'

        reactor.run()

    @inlineCallbacks
    def run_server(redis):
        root_logger.debug('Running server')

        eb = EventBus(redis)
        root_logger.debug('Connecting event bus')
        yield eb.connect()

        root_logger.debug('Configuring injector.')

        def my_config(binder):
            binder.bind(txredisapi.Connection, redis)
            binder.bind(EventBus, eb)
            binder.bind(IDockerClient, DockerTwistedClient())

            binder.bind('dns-server', dns_server_ip)
            binder.bind('dns-search-suffix', dns_prefix)

        # Configure a shared injector.
        inject.configure(my_config)

        root_logger.debug('Starting rpc listener')

        # rpc
        listen_rpc()

        root_logger.debug('Dumping resolv conf')

        # dns
        dump_resolv_conf(dns_server_ip)

        root_logger.debug('Listen dns')
        listen_dns(dns_prefix, dns_server_ip, 53)

        root_logger.debug('Dns plugin')
        DnsPlugin()


        if args.haproxy:
            root_logger.debug('Haproxy plugin')
            HaproxyPlugin()

        root_logger.debug('Monitor plugin')
        DockerMonitorPlugin()

        root_logger.debug('Started.')

    def timeout():
        print('Can not connect to redis!')
        reactor.stop()

    txtimeout(txredisapi.Connection(dbid=1), 3, timeout).addCallback(run_server)

    reactor.run()


if __name__ == '__main__':
    entry_point()