"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

* This code was written entirely by VMware Inc.  It has been restructured
* and slightly modified, to for specific use at example, Inc.  example
* Inc. assumes no credit!
"""


__author__ = "VMWare, Inc."
__vcenter_version__ = '6.5+'


# Python Libraries
from com.vmware.vcenter.vm.hardware.boot_client import Device as BootDevice
from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter.vm_client import (Hardware, Power)
from com.vmware.vcenter_client import VM
from com.vmware.vcenter.vm.hardware_client import (
    Cpu, Memory, Disk, Ethernet, Cdrom, Serial, Parallel, Floppy, Boot, ScsiAddressSpec)


# provisioner
from provisioner.core.config import configmanager
from provisioner.core.connection.baseutilities import pp
from provisioner.core.connection.connectionhelpers import get_distributed_network_backing, \
    get_standard_network_backing, get_placement_spec_for_resource_pool, get_vm, get_unverified_session


class CreateExhaustiveVM(object):

    def __init__(self, hostname, cpu, ram, disk, client=None, placement_spec=None,
                 standard_network=None, distributed_network=None):

        self.hostname = hostname
        self.cpu = cpu
        self.ram = ram
        self.disk = disk
        self.client = client
        self.placement_spec = placement_spec
        self.standard_network = standard_network
        self.distributed_network = distributed_network
        self.vm_name = self.hostname
        self.cleardata = None

        # Execute the sample in standalone mode.
        if not self.client:
            session = get_unverified_session()
            self.client = create_vsphere_client(server=configmanager.config['SERVER'],
                                                username=configmanager.config['USERNAME'],
                                                password=configmanager.config['PASSWORD'],
                                                session=session)

    def run(self):
        # Get a placement spec
        datacenter_name = configmanager.config['VM_DATACENTER_NAME']
        vm_folder_name = configmanager.config['VM_FOLDER2_NAME']
        datastore_name = configmanager.config['VM_DATASTORE_NAME']
        std_portgroup_name = configmanager.config['STDPORTGROUP_NAME']
        dv_portgroup_name = configmanager.config['VDPORTGROUP1_NAME']

        if not self.placement_spec:
            self.placement_spec = get_placement_spec_for_resource_pool(
                self.client,
                datacenter_name,
                vm_folder_name,
                datastore_name)

        # Get a standard network backing
        if not self.standard_network:
            self.standard_network = get_standard_network_backing(
                self.client,
                std_portgroup_name,
                datacenter_name)

        # Get a distributed network backing
        if not self.distributed_network:
            self.distributed_network = get_distributed_network_backing(
                self.client,
                dv_portgroup_name,
                datacenter_name)

        guest_os = configmanager.config['VM_GUESTOS']
        iso_datastore_path = configmanager.config['ISO_DATASTORE_PATH']
        serial_port_network_location = \
            configmanager.config['SERIAL_PORT_NETWORK_SERVER_LOCATION']

        GiB = 1024 * 1024 * 1024
        GiBMemory = 1024

        vm_create_spec = VM.CreateSpec(
            guest_os=guest_os,
            name=self.vm_name,
            placement=self.placement_spec,
            hardware_version=Hardware.Version.VMX_11,
            cpu=Cpu.UpdateSpec(count=self.cpu,
                               cores_per_socket=self.cpu,
                               hot_add_enabled=False,
                               hot_remove_enabled=False),
            memory=Memory.UpdateSpec(size_mib=self.ram * GiBMemory,
                                     hot_add_enabled=False),
            disks=[
                Disk.CreateSpec(type=Disk.HostBusAdapterType.SCSI,
                                scsi=ScsiAddressSpec(bus=0, unit=0),
                                new_vmdk=Disk.VmdkCreateSpec(name='data1',
                                                             capacity=self.disk * GiB))
            ],
            nics=[
                Ethernet.CreateSpec(
                    start_connected=True,
                    mac_type=Ethernet.MacAddressType.GENERATED,
                    backing=Ethernet.BackingSpec(
                        type=Ethernet.BackingType.STANDARD_PORTGROUP,
                        network=self.standard_network))
            ],
            cdroms=[
                Cdrom.CreateSpec(
                    start_connected=True,
                    backing=Cdrom.BackingSpec(type=Cdrom.BackingType.ISO_FILE,
                                              iso_file=iso_datastore_path)
                )
            ],
            serial_ports=[
                Serial.CreateSpec(
                    start_connected=False,
                    backing=Serial.BackingSpec(
                        type=Serial.BackingType.NETWORK_SERVER,
                        network_location=serial_port_network_location)
                )
            ],
            parallel_ports=[
                Parallel.CreateSpec(
                    start_connected=False,
                    backing=Parallel.BackingSpec(
                        type=Parallel.BackingType.HOST_DEVICE)
                )
            ],
            floppies=[
                Floppy.CreateSpec(
                    backing=Floppy.BackingSpec(
                        type=Floppy.BackingType.CLIENT_DEVICE)
                )
            ],
            boot=Boot.CreateSpec(type=Boot.Type.BIOS,
                                 delay=0,
                                 enter_setup_mode=False
                                 ),
            # TODO Should DISK be put before CDROM and ETHERNET?  Does the BIOS
            # automatically try the next device if the DISK is empty?
            boot_devices=[
                BootDevice.EntryCreateSpec(BootDevice.Type.CDROM),
                BootDevice.EntryCreateSpec(BootDevice.Type.DISK),
                BootDevice.EntryCreateSpec(BootDevice.Type.ETHERNET)
            ]
        )
        print(
            '# Example: create_exhaustive_vm: Creating a VM using spec\n-----')
        print(pp(vm_create_spec))
        print('-----')

        vm = self.client.vcenter.VM.create(vm_create_spec)

        print("create_exhaustive_vm: Created VM '{}' ({})".format(self.vm_name,
                                                                  vm))

        vm_info = self.client.vcenter.VM.get(vm)
        print('vm.get({}) -> {}'.format(vm, pp(vm_info)))

        return vm

    def cleanup(self):
        vm = get_vm(self.client, self.vm_name)
        if vm:
            state = self.client.vcenter.vm.Power.get(vm)
            if state == Power.Info(state=Power.State.POWERED_ON):
                self.client.vcenter.vm.Power.stop(vm)
            elif state == Power.Info(state=Power.State.SUSPENDED):
                self.client.vcenter.vm.Power.start(vm)
                self.client.vcenter.vm.Power.stop(vm)
            print("Deleting VM '{}' ({})".format(self.vm_name, vm))
            self.client.vcenter.VM.delete(vm)
