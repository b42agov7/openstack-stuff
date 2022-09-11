#!/usr/bin/env python3
# -*- coding: utf-8 -*
# version 0.1
# author: b42agov7
# 2022-07-29

import config
import openstack
from openstack import connection
import time
import subprocess

# Variables to set up the "parameters" for an instance creation.
flavor_name = 'cirros-no-dpdk'
image_name = 'cirros-image'
network_name = 'b-network'
subnet_name = 'b-subnet'

# Create a clouds.yaml file.
config.generate_cloud_file()

# Function to delete an instance with an error state.
def delete_instance_error():
    bash_command = 'source /home/stack/overcloudrc && for i in $(openstack server list --status error | cut -d " " -f 2 | grep "^[a-z1-9]"); do openstack server delete ${i}; done'
    pipe = subprocess.Popen(['/bin/bash', '-c', '%s' %(bash_command)], stdout=subprocess.PIPE)

# Connect to cloud "overcloud".
conn = openstack.connect(cloud="overcloud")

# Delete instances with an error state.
try:
    delete_instance_error()
except AttributeError:
    print("[+] No instances to delete.")

# Delete a flavor.
try:
    flavor_to_delete = conn.compute.find_flavor(flavor_name)
    conn.compute.delete_flavor(flavor_to_delete.id)
    print("[+] Flavor deleted.")
except AttributeError:
    print("[+] No flavor to delete.")

# Delete an image.
try:
    image_to_delete = conn.image.find_image(image_name)
    conn.image.delete_image(image_to_delete.id)
    print("[+] Image deleted")
except AttributeError:
    print("[+] No image to delete")
    
# Delete a network and a subnet.
try:
    network_to_delete = conn.network.find_network(network_name)
    conn.network.delete_network(network_to_delete.id)
    print("[+] Network deleted")
    conn.network.delete_subnet(subnet_name)
    print("[+] Subnet deleted")
except AttributeError:
    print("[+] No network or subnet to delete.")

# Delete clouds.yaml file.
config.delete_cloud_file()