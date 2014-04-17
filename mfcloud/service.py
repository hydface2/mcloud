import logging
import inject
from mfcloud.txdocker import IDockerClient

logger = logging.getLogger('mfcloud.application')

class NotInspectedYet(Exception):
    pass


class Service(object):

    NotInspectedYet = NotInspectedYet

    client = inject.attr(IDockerClient)

    image_builder = None
    name = None
    volumes = None
    command = None
    env = None
    config = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        super(Service, self).__init__()

        self._inspect_data = None
        self._inspected = False

    def build_docker_config(self):
        pass

    def inspect(self):

        d = self.client.find_container_by_name(self.name)

        d.addCallback(self.client.inspect)

        def save_inspect_data(data):
            self._inspect_data = data
            self._inspected = True
            return data

        d.addCallback(save_inspect_data)

        return d

    def is_running(self):
        if not self.is_inspected():
            raise self.NotInspectedYet()

        try:
            return self.is_created() and self._inspect_data['State']['Running']
        except KeyError:
            return False

    def is_created(self):
        if not self.is_inspected():
            raise self.NotInspectedYet()

        return not self._inspect_data is None

    def start(self, ticket_id):

        d = self.client.find_container_by_name(self.name)

        logger.debug('[%s][%s] Starting service' % (ticket_id, self.name))

        def on_result(id):
            logger.debug('[%s][%s] Service resolve by name result: %s' % (ticket_id, self.name, id))

            def start(*args):
                logger.debug('[%s][%s] Starting service...' % (ticket_id, self.name))
                return self.client.start_container(id, ticket_id=ticket_id)

            if not id:
                logger.debug('[%s][%s] Service not created. Creating ...' % (ticket_id, self.name))
                d = self.create(ticket_id)
                d.addCallback(start, ticket_id)
                return d
            else:
                return start()

        d.addCallback(on_result)
        d.addCallback(lambda *args: self.inspect())

        return d

    def stop(self, ticket_id):

        d = self.client.find_container_by_name(self.name)

        def on_result(id):
            return self.client.stop_container(id, ticket_id=ticket_id)

        d.addCallback(on_result)
        d.addCallback(lambda *args: self.inspect())

        return d

    def create(self, ticket_id):

        d = self.image_builder.build_image(ticket_id=ticket_id)

        def image_ready(image_name):
            config = {
                "Hostname": self.name,
                "Image": image_name
            }

            return self.client.create_container(config, self.name, ticket_id=ticket_id)

        d.addCallback(image_ready)
        d.addCallback(lambda *args: self.inspect())

        return d

    def destroy(self, ticket_id):

        d = self.client.find_container_by_name(self.name)

        def on_result(id):
            return self.client.remove_container(id, ticket_id=ticket_id)

        d.addCallback(on_result)
        d.addCallback(lambda *args: self.inspect())

        return d

    def is_inspected(self):
        return self._inspected




