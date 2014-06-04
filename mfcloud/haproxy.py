
import json
import logging
import sys
import inject
from mfcloud.util import txtimeout
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
import txredisapi
from txzmq import ZmqFactory, ZmqEndpoint, ZmqSubConnection

HAPROXY_TPL = """
global
        log /dev/log    local0
        log /dev/log    local1 notice
        chroot /var/lib/haproxy
        user haproxy
        group haproxy
        daemon

defaults
        log     global
        mode    http
        option  httplog
        option  dontlognull
        contimeout 5000
        clitimeout 50000
        srvtimeout 50000
        errorfile 400 /etc/haproxy/errors/400.http
        errorfile 403 /etc/haproxy/errors/403.http
        errorfile 408 /etc/haproxy/errors/408.http
        errorfile 500 /etc/haproxy/errors/500.http
        errorfile 502 /etc/haproxy/errors/502.http
        errorfile 503 /etc/haproxy/errors/503.http
        errorfile 504 /etc/haproxy/errors/504.http

frontend http_proxy
  bind 0.0.0.0:80

  {% for app in apps %}
  {% for domain in app.domains %}
  acl is_{{ app.name }} hdr_dom(host) -i {{ domain }}{% endfor %}
  use_backend {{ app.name }}_cluster if is_{{ app.name }}
  {% endfor %}

{% for app in apps %}
backend {{ app.name }}_cluster
  {% for backend in app.backends %}server {{ backend.name }} {{ backend.ip }}:{{ backend.port }}{% endfor %}
{% endfor %}
"""

from jinja2 import Environment as JinjaEnv, StrictUndefined, Template


class HaproxyConfig(object):

    redis = inject.attr(txredisapi.Connection)

    def __init__(self, path, template=None, internal_suffix='mfcloud.lh'):
        self.template = template
        self.path = path
        self.internal_suffix = internal_suffix



    def dump(self, containers, apps_list):

        template = self.template

        if not template:
            template = Template(HAPROXY_TPL)

        print apps_list

        apps = {}

        for container in containers:
            name_ = container['Name']
            if name_[0] == '/':
                name_ = name_[1:]

            name_ = '.'.join([name_, self.internal_suffix])
            apps[name_] = container['NetworkSettings']['IPAddress']

        logging.info('Installing new app list: %s' % str(apps))

        if len(apps) > 1:
            return self.redis.hmset('domain', apps)
        elif len(apps) == 1:
            return self.redis.hset('domain', apps.keys()[0], apps.values()[0])




            # apps.append({
            #     'name': re.sub('[^a-z0-9_]', '_', conf['domain']),
            #     'domains': [conf['domain']],
            #     'backends': [{
            #                      'name': 'backend_%s' % i,
            #                      'ip': x[0],
            #                      'port': x[1]
            #                  } for i, x in enumerate(conf['backends'])]
            # })

        #
        #
        #
        # template = Template(HAPROXY_TPL)
        #
        # with open(path, 'w') as f:
        #     f.write(template.render({'apps': apps}))
        #
        # os.system('service haproxy reload')

def entry_point():

    console_handler = logging.StreamHandler(stream=sys.stderr)
    console_handler.setFormatter(logging.Formatter())
    console_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)
    root_logger.debug('Logger initialized')

    import argparse

    parser = argparse.ArgumentParser(description='Websocket server')
    parser.add_argument('--endpoint', type=str, default=['tcp://127.0.0.1:5555'], nargs='+', help='ip address')
    args = parser.parse_args()

    def run_server(redis):
        config = HaproxyConfig(path='/etc/haproxy/haproxy.cfg')

        def on_message(message, tag):
            if tag == 'event-containers-updated':
                data = json.loads(message)
                config.dump(data['list'], data['apps'])

        zf2 = ZmqFactory()

        for endpoint in args.endpoint:
            subscribe_con = ZmqSubConnection(zf2, ZmqEndpoint('connect', endpoint))
            subscribe_con.subscribe("")
            subscribe_con.gotMessage = on_message

        def my_config(binder):
            binder.bind(txredisapi.Connection, redis)

        # Configure a shared injector.
        inject.configure(my_config)

    def timeout():
        print('Can not connect to redis!')
        reactor.stop()

    txtimeout(txredisapi.Connection(dbid=1), 3, timeout).addCallback(run_server)



    reactor.run()

if __name__ == '__main__':
    entry_point()