from provisioner.core.connection.connectionbase import GoogleConnection
from provisioner.core.utilities.FrozenJSON import FrozenJSON
from provisioner.core.utilities.asynchronous import AsynchronousRoutine
from provisioner.core.utilities.cache import CheckCache

import googleapiclient.discovery
import os


@CheckCache(seconds=55000, cache_dir='/tmp/cache_directory')
def list_instances(compute, project, zone):
    res = compute.instances().list(project=project, zone=zone).execute()
    if not res.get('items', False) is not None:
        return None
    return res['items']


def create_instance(compute, project, zone, name, image_project='centos-7-v20190619', image_family='centos-7', bucket=None):

    image_response = compute.images().getFromFamily(
        project=image_project, family=image_family
    ).execute()

    source_disk_image = image_response['selfLink']

    machine_type = "zones/{}/machineTypes/n1-standard-1".format(zone)

    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup_script.sh'), 'r').read()

    config = {

        'name': name,
        'machineType': machine_type,

        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image
                }
            }
        ],
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }]
    }


@CheckCache(seconds=85000, cache_dir='/tmp/cache_directory')
def get_gcp_instances(project=None, zone=None):
    gcp_master_set = []
    if project is None or zone is None:
        raise ValueError('Must supply \'zone\' and \'project\'\
        for this request!')

    request_string = 'https://www.googleapis.com/compute/v1/projects/{}/zones/{}/instances'.format(
        project, zone
    )

    data = GoogleConnection.stringapi(request_string)
    data = FrozenJSON(data)

    # return an immutable tuple of instance name, zone
    # pass the instance object to a callback function
    # for asynchronous handling of data

    @CheckCache(seconds=3600, cache_dir='/tmp/cache_directory')
    def build_data_tuple(instance_data_set):
        instance_name = instance_data_set.items[0].name
        instance_zone = instance_data_set.items[4]
        instance_status = instance_data_set.items[2]
        stored_object = (instance_name, instance_zone, instance_status)
        return stored_object

    data_set = list(data)
    for _ in range(10):
        job = AsynchronousRoutine(data_set[:10], build_data_tuple)
        del data_set[:10]
        gcp_master_set.append(job)

    return gcp_master_set