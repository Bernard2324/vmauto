from com.vmware.vcenter_client import Cluster, Datacenter, Datastore, Folder, Network, ResourcePool, VM
import ssl
import requests
import urllib3

def get_cluster(client, datacenter_name, cluster_name):
    """
    Returns the identifier of a cluster
    Note: The method assumes only one cluster and datacenter
    with the mentioned name.
    """

    datacenter = get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter_spec = Cluster.FilterSpec(names=set([cluster_name]),
                                     datacenters=set([datacenter]))

    cluster_summaries = client.vcenter.Cluster.list(filter_spec)
    if len(cluster_summaries) > 0:
        cluster = cluster_summaries[0].cluster
        print("Detected cluster '{}' as {}".format(cluster_name, cluster))
        return cluster
    else:
        print("Cluster '{}' not found".format(cluster_name))
        return None


def get_datacenter(client, datacenter_name):
    """
    Returns the identifier of a datacenter
    Note: The method assumes only one datacenter with the mentioned name.
    """

    filter_spec = Datacenter.FilterSpec(names=set([datacenter_name]))

    datacenter_summaries = client.vcenter.Datacenter.list(filter_spec)
    if len(datacenter_summaries) > 0:
        datacenter = datacenter_summaries[0].datacenter
        return datacenter
    else:
        return None


def get_datastore(client, datacenter_name, datastore_name):
    """
    Returns the identifier of a datastore
    Note: The method assumes that there is only one datastore and datacenter
    with the mentioned names.
    """
    datacenter = get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter_spec = Datastore.FilterSpec(names=set([datastore_name]),
                                       datacenters=set([datacenter]))

    datastore_summaries = client.vcenter.Datastore.list(filter_spec)
    if len(datastore_summaries) > 0:
        datastore = datastore_summaries[0].datastore
        return datastore
    else:
        return None
    
def get_folder(client, datacenter_name, folder_name):
    """
    Returns the identifier of a folder
    Note: The method assumes that there is only one folder and datacenter
    with the mentioned names.
    """
    datacenter = get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter_spec = Folder.FilterSpec(type=Folder.Type.VIRTUAL_MACHINE,
                                    names=set([folder_name]),
                                    datacenters=set([datacenter]))

    folder_summaries = client.vcenter.Folder.list(filter_spec)
    if len(folder_summaries) > 0:
        folder = folder_summaries[0].folder
        print("Detected folder '{}' as {}".format(folder_name, folder))
        return folder
    else:
        print("Folder '{}' not found".format(folder_name))
        return None


def get_standard_network_backing(client,
                                 std_porggroup_name,
                                 datacenter_name):
    """
    Gets a standard portgroup network backing for a given Datacenter
    Note: The method assumes that there is only one standard portgroup
    and datacenter with the mentioned names.
    """
    datacenter = get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter = Network.FilterSpec(datacenters=set([datacenter]),
                                names=set([std_porggroup_name]),
                                types=set([Network.Type.STANDARD_PORTGROUP]))
    network_summaries = client.vcenter.Network.list(filter=filter)

    if len(network_summaries) > 0:
        network = network_summaries[0].network
        print("Selecting Standard Portgroup Network '{}' ({})".
              format(std_porggroup_name, network))
        return network
    else:
        print("Standard Portgroup Network not found in Datacenter '{}'".
              format(datacenter_name))
        return None


def get_distributed_network_backing(client,
                                    dv_portgroup_name,
                                    datacenter_name):
    """
    Gets a distributed portgroup network backing for a given Datacenter
    Note: The method assumes that there is only one distributed portgroup
    and datacenter with the mentioned names.
    """
    datacenter = get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter = Network.FilterSpec(datacenters=set([datacenter]),
                                names=set([dv_portgroup_name]),
                                types=set([Network.Type.DISTRIBUTED_PORTGROUP]))
    network_summaries = client.vcenter.Network.list(filter=filter)

    if len(network_summaries) > 0:
        network = network_summaries[0].network
        print("Selecting Distributed Portgroup Network '{}' ({})".
              format(dv_portgroup_name, network))
        return network
    else:
        print("Distributed Portgroup Network not found in Datacenter '{}'".
              format(datacenter_name))
        return None


def get_resource_pool(client, datacenter_name, resource_pool_name=None):
    """
    Returns the identifier of the resource pool with the given name or the
    first resource pool in the datacenter if the name is not provided.
    """
    datacenter = get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    names = set([resource_pool_name]) if resource_pool_name else None
    filter_spec = ResourcePool.FilterSpec(datacenters=set([datacenter]),
                                          names=names)

    resource_pool_summaries = client.vcenter.ResourcePool.list(filter_spec)
    if len(resource_pool_summaries) > 0:
        resource_pool = resource_pool_summaries[0].resource_pool
        print("Selecting ResourcePool '{}'".format(resource_pool))
        return resource_pool
    else:
        print("ResourcePool not found in Datacenter '{}'".
              format(datacenter_name))
        return None


def get_vm(client, vm_name):
    """
    Return the identifier of a vm
    Note: The method assumes that there is only one vm with the mentioned name.
    """
    names = set([vm_name])
    vms = client.vcenter.VM.list(VM.FilterSpec(names=names))

    if len(vms) == 0:
        print("VM with name ({}) not found".format(vm_name))
        return None

    vm = vms[0].vm
    print("Found VM '{}' ({})".format(vm_name, vm))
    return vm


def get_vms(client, vm_names):
    """Return identifiers of a list of vms"""
    vms = client.vcenter.VM.list(VM.FilterSpec(names=vm_names))

    if len(vms) == 0:
        print('No vm found')
        return None

    print("Found VMs '{}' ({})".format(vm_names, vms))
    return vms


def get_placement_spec_for_resource_pool(client,
                                         datacenter_name,
                                         vm_folder_name,
                                         datastore_name):
    """
    Returns a VM placement spec for a resourcepool. Ensures that the
    vm folder and datastore are all in the same datacenter which is specified.
    """
    resource_pool = get_resource_pool(client,
                                                           datacenter_name)

    folder = get_folder(client,
                                      datacenter_name,
                                      vm_folder_name)

    datastore = get_datastore(client, datacenter_name, datastore_name)

    # Create the vm placement spec with the datastore, resource pool and vm
    # folder
    placement_spec = VM.PlacementSpec(folder=folder,
                                      resource_pool=resource_pool,
                                      datastore=datastore)

    print("get_placement_spec_for_resource_pool: Result is '{}'".
          format(placement_spec))
    return placement_spec


def get_unverified_context():
    """
    Get an unverified ssl context. Used to disable the server certificate
    verification.
    @return: unverified ssl context.
    """
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    return context


def get_unverified_session():
    """
    Get a requests session with cert verification disabled.
    Also disable the insecure warnings message.
    Note this is not recommended in production code.
    @return: a requests session with verification disabled.
    """
    session = requests.session()
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # requests.packages.urllib3.disable_warnings()
    return session
