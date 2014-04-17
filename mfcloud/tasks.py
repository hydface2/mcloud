import logging
import inject
from mfcloud.application import ApplicationController, Application
from twisted.internet import defer, reactor
from twisted.internet.defer import Deferred, DeferredList


logger = logging.getLogger('mfcloud.tasks')

class TaskService():
    app_controller = inject.attr(ApplicationController)
    """
    @type app_controller: ApplicationController
    """

    def task_init_app(self, ticket_id, name, path):

        d = self.app_controller.create(name, path)

        def done(app):
            return not app is None

        d.addCallback(done)
        return d

    def task_list_app(self, ticket_id):
        d = self.app_controller.list()

        def done(apps):
            return [(name, apps.config['path']) for name, apps in apps.items()]

        d.addCallback(done)
        return d

    def task_del_app(self, ticket_id, name):
        d = self.app_controller.remove(name)

        # d.addCallback(done)
        return d

    def task_app_status(self, ticket_id, name):
        d = self.app_controller.get(name)

        def on_result(config):
            """
            @type config: YamlConfig
            """

            data = []
            for service in config.get_services().values():
                """
                @type service: Service
                """

                assert service.is_inspected()

                data.append([
                    service.name,
                    service.is_running(),
                    service.is_running()
                ])

            return data

        d.addCallback(lambda app: app.load())
        d.addCallback(on_result)
        return d

    def task_app_start(self, ticket_id, name):

        logger.debug('[%s] Starting application' % (ticket_id, ))

        d = self.app_controller.get(name)

        def on_result(config):
            """
            @type config: YamlConfig
            """

            logger.debug('[%s] Got response' % (ticket_id, ))

            d = []
            for service in config.get_services().values():
                if not service.is_running():
                    logger.debug('[%s] Service %s is not running. Starting' % (ticket_id, service.name))
                    d.append(service.start(ticket_id))
                else:
                    logger.debug('[%s] Service %s is already running.' % (ticket_id, service.name))

            return DeferredList(d)

        d.addCallback(lambda app: app.load())
        d.addCallback(on_result)
        return d

    def task_app_stop(self, ticket_id, name):

        logger.debug('[%s] Stoping application' % (ticket_id, ))

        d = self.app_controller.get(name)

        def on_result(config):
            """
            @type config: YamlConfig
            """

            logger.debug('[%s] Got response' % (ticket_id, ))

            d = []
            for service in config.get_services().values():
                if service.is_running():
                    logger.debug('[%s] Service %s is running. Stoping' % (ticket_id, service.name))
                    d.append(service.stop(ticket_id))
                else:
                    logger.debug('[%s] Service %s is already stopped.' % (ticket_id, service.name))

            return DeferredList(d)

        d.addCallback(lambda app: app.load())
        d.addCallback(on_result)
        return d

    def task_app_service_inspect(self, ticket_id, name, service_name):

        logger.debug('[%s] Inspecting application service %s' % (ticket_id, service_name))

        d = self.app_controller.get(name)

        def on_result(config):
            """
            @type config: YamlConfig
            """
            logger.debug('[%s] Got response' % (ticket_id, ))

            service = config.get_service(service_name)
            if not service.is_running():
                return 'Not running'
            else:
                if not service.is_inspected():
                    return service.inspect()
                else:
                    return service._inspect_data


        d.addCallback(lambda app: app.load())
        d.addCallback(on_result)
        return d

    def register(self, rpc_server):

        rpc_server.tasks.update({
            'init': self.task_init_app,
            'list': self.task_list_app,
            'status': self.task_app_status,
            'inspect': self.task_app_service_inspect,
            'start': self.task_app_start,
            'stop': self.task_app_stop,
            'remove': self.task_del_app,
        })