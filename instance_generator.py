#!/usr/bin/env python3
# -*- coding: utf-8 -*
# version 0.1
# author: b42agov7
# 2022-07-29

import config
import openstack
from openstack import connection
import time
import os
import sys
import datetime
import subprocess

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

# Set the parameters.
if conn.image.find_image(image_name) is None:
    print("[-] Error occured!\n[i] Can't create an image...")
else:
    instance_image = conn.image.find_image(image_name)

if conn.compute.find_flavor(flavor_name) is None:
    print("[-] Error occured!\n[i] Can't create a flavor...")
else:
    instance_flavor = conn.compute.find_flavor(flavor_name)

if conn.network.find_network(network_name) is None:
    print("[-] Error occured!\n[i] Can't create a network and a subnet...")
else:
    instance_network = conn.network.find_network(network_name)

# Function to create an instance.
def create_instance(name_p):
    instance_to_create = conn.compute.create_server(name=name_p, image_id=instance_image.id, flavor_id=instance_flavor.id, networks=[{"uuid": instance_network.id}])
    instance_to_create = conn.compute.wait_for_server(instance_to_create)
    return instance_to_create.id

# Function to delete an instace.
def delete_instance(name_p):
    instance_to_remove = conn.compute.delete_server(name_p)

# Function to delete an instance with an error state.
def delete_instance_error():
    bash_command = 'source /home/stack/overcloudrc && for i in $(openstack server list --status error | cut -d " " -f 2 | grep "^[a-z1-9]"); do openstack server delete ${i}; done'
    pipe = subprocess.Popen(['/bin/bash', '-c', '%s' %(bash_command)], stdout=subprocess.PIPE)

# Infinite loop to create instances.
id = 0
name = "instance_"
state_up = False
instance_list = []

print("[i] To stop the script, just press Ctrl + C and wait few seconds.")
while True:
    instance_name = name + str(id)
    conn = openstack.connect(cloud="overcloud")
    try:
        instance = create_instance(instance_name)
        instance_list.append(instance)
        if state_up == False:
            now = datetime.datetime.now()
            up = (now.strftime("%d/%m/%Y at %H:%M:%S - The computes are up."))
            file = open("instance_generator.log", "a")
            file.write(up + "\n")
            file.close()
        print("[+] " + instance_name + " created.")
        time.sleep(4)
        print('\033[F', end='')
        delete_instance(instance)
        print("[+] " + instance_name + " deleted.")
        instance_list.remove(instance)
        time.sleep(2)
        print('\033[F', end='')
        state_up = True
    except KeyboardInterrupt:
        print("\n[+] Stop the script.\n[+] Try to clear the last instance.")
        time.sleep(15)
        break
    except openstack.exceptions.ResourceTimeout:
        print("[-] Error occured, can't create an instance. Resource timeout.")
        print('\033[F', end='')
        now = datetime.datetime.now()
        down = (now.strftime("%d/%m/%Y at %H:%M:%S - Can't create an instance, the computes are down."))
        file = open("instance_generator.log", "a")
        file.write(down + "\n")
        file.close()
    except openstack.exceptions.ResourceFailure:
        print("[-] Error occured, can't create an instance. Resource failure.")
        print('\033[F', end='')
    except openstack.exceptions.HttpException:
        print("[-] Error occured, can't create an instance. The computes are down.\n")
        state_up = False
        time.sleep(2)
        print('\033[F', end='')
        delete_instance_error()
        time.sleep(40)
    id += 1

# Clear the last instance.
last_instance = conn.compute.find_server(instance_name)
try:
    instance_list.append(last_instance.id)
except AttributeError:
    print("[+] No instances to delete.")
for instance in instance_list:
    delete_instance(instance)

# Delete clouds.yaml file.
config.delete_cloud_file()
