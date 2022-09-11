#!/usr/bin/env python3
# -*- coding: utf-8 -*
# version 0.1
# author: b42agov7
# 2022-07-27

import config
import openstack
from openstack import connection

# Variables to set up the "parameters" for an instance creation.
flavor_name = 'cirros-no-dpdk'
image_name = 'cirros-image'
image_path = 'image/cirros-0.5.1-x86_64-disk.img'
network_name = 'b-network'
subnet_name = 'b-subnet'

# Create a clouds.yaml file.
config.generate_cloud_file()

# Connect to cloud "overcloud".
conn = openstack.connect(cloud="overcloud")

# Create a flavor.
print("[+] Create a flavor if not exists.")
if conn.compute.find_flavor(flavor_name) is None:
    conn.compute.create_flavor(name=flavor_name, ram='1024', disk='0', vcpus='2')
    print("[+] Flavor created.")

# Create an image.
print("[+] Create an image if not exists.")
if conn.image.find_image(image_name) is None:
    conn.image.create_image(name=image_name, filename=image_path, disk_format='qcow2', container_format='bare', visibility='public')
    print("[+] Image created.")

# Create a network and a subnet.
print("[+] Create a network and a subnet if not exists.")
network = conn.network.find_network(network_name)
if network is None:
    network = conn.network.create_network(name=network_name, is_admin_state_up=True)
    subnet = conn.network.create_subnet(network_id=network.id, cidr='1.1.1.0/24', ip_version=4, subnet_name=subnet_name)
    print("[+] Network and subnet created.")

print("[+] Create two instances.")

# Set the parameters.
if conn.image.find_image(image_name) is None:
    print("[-] Error occured!\nCan't create an image...")
else:
    instance_image = conn.image.find_image(image_name)

if conn.compute.find_flavor(flavor_name) is None:
    print("[-] Error occured!\nCan't create a flavor...")
else:
    instance_flavor = conn.compute.find_flavor(flavor_name)

if conn.network.find_network(network_name) is None:
    print("[-] Error occured!\nCan't create a network and a subnet...")
else:
    instance_network = conn.network.find_network(network_name)

# Create instances.
instance_0 = conn.compute.create_server(name="create_instance_0", image_id=instance_image.id, flavor_id=instance_flavor.id, networks=[{"uuid": instance_network.id}])
instance_0 = conn.compute.wait_for_server(instance_0)

instance_1 = conn.compute.create_server(name="create_instance_1", image_id=instance_image.id, flavor_id=instance_flavor.id, networks=[{"uuid": instance_network.id}])
instance_1 = conn.compute.wait_for_server(instance_1)

print("[i] Creation done. Bye! :)")

# Delete clouds.yaml file.
config.delete_cloud_file()