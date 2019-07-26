from provisioner.core.config.configmanager import WebConfig
from provisioner.core.utilities.cache import CheckCache
from chef import ChefAPI, Node
from celery import Celery


def JobQueue(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


class ChefNodes(object):

    def __init__(self):
        self.chef_server = 'https://chef.sub.example.com/organizations/example'

    @CheckCache(seconds=2400, cache_dir='/tmp/cache_directory')
    def GetNodes(self):
        node_data = {}
        with ChefAPI(self.chef_server, 'adminuser.pem', 'admin', ssl_verify=False):
            for node in Node.list():
                nobeobj = Node(node)
                node_data[node] = nobeobj.to_dict()
        return node_data