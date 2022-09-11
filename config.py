#!/usr/bin/env python3
# -*- coding: utf-8 -*
# version 0.1
# author: b42agov7
# 2022-07-25

import os
import subprocess
import json
from jinja2 import Environment, FileSystemLoader

# OpenStack directory. 
openstack_data = "/etc/openstack"

# undercloud file.
undercloud_file = {
    "path": "/home/stack/stackrc",
    "name": "stackrc",
    "url_append": "/v3"
}

# overcloud file.
overcloud_file = {
    "path": "/home/stack/overcloudrc",
    "name": "overcloud",
    "url_append": "/v3"
}

# Function to extract all necessary data.
def data_extrat(filedata):
    source = 'source {}'.format(filedata['path'])
    dump = \
        '/usr/bin/python3 -c "import os, json;print(json.dumps(dict(os.environ)))"'
    pipe = subprocess.Popen(['/bin/bash', '-c', '%s && %s' %(source, dump)], stdout=subprocess.PIPE)
    env = json.loads(pipe.stdout.read())
    os.environ = env
    return {
        'name': filedata['name'],
        'username': os.getenv('OS_USERNAME'),
        'password': os.getenv('OS_PASSWORD'),
        'project': os.getenv('OS_PROJECT_NAME'),
        'url': os.getenv('OS_AUTH_URL') + filedata['url_append'],
        'user_domain': os.getenv('OS_USER_DOMAIN_NAME'),
        'project_domain': os.getenv('OS_PROJECT_DOMAIN_NAME')
    }

# Function to check if the "clouds.yaml" file exists.
def cloud_file_exists():
    exists = os.path.exists(openstack_data + "/clouds.yaml")
    if exists:
        return True
    else:
        return False

# Function to create a custom "clouds.yaml" file.
def generate_cloud_file():
    if not cloud_file_exists():
        print("[+] Generating a cloud file.")
        file_loader = FileSystemLoader("templates")
        j2 = Environment(loader=file_loader)
        template = j2.get_template("clouds.yaml.j2")
        output = template.render(
        clouds=[data_extrat(undercloud_file),data_extrat(overcloud_file)])
        with open(openstack_data + '/clouds.yaml', 'w') as cloudfile:
            cloudfile.write(output)

# Function to delete the previous "clouds.yaml" file.
def delete_cloud_file():
    if cloud_file_exists():
        print("[+] Deleting cloud file.")
        file_path = openstack_data + '/clouds.yaml'
        os.remove(file_path)