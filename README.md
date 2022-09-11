# openstack-stuff

These Python scripts permit to create 2 instances 
or to create instances into overcloud  in the aim to detect
a service impact with your computes if it's going to be down for example.
During the instance creation, a flavor, a network and a subnet will be
created. An image will be also uploaded.
The image used by the script is Cirros.

*Note that the script creates a flavor for a no dpdk compute!*

These scripts must run with super user rights (use sudo or doas).

**Make a backup of /etc/openstack/clouds.yaml, because the scripts will generate
a new /etc/openstack/clouds.yaml file to connect
towards overcloud cloud and then delete it at the end.**

*Note that you can call the generate_cloud_file() function from config.py
to create dynamically a /etc/openstack/clouds.yaml file.*

## What the scripts do

- **config.py** is used by all the scripts to generate and delete a clouds.yaml file.
- **create.py** creates 2 instances.
- **instance_generator.py** create instances as an infinite way until you 
stop it. An instance_generator.log file is also created.
- **clear.py**  must be run after the deletion of the two instances 
created by create.py!
clear.py deletes the instances with an error state as well as flavor,
image, network and subnet created by create.py or instance_generator.py
scripts.

## Requirements

```bash
pip3 install -r requirements.txt
```

## Setup

Download the Cirros image from [OpenStack](https://docs.openstack.org/image-guide/obtain-images.html#cirros-test) website 
and put it into image directory. Then edit the <image_path> variable in all scripts if you download a newer version of Cirros.

From your director node, make the scripts executable, then run create.py, instance_generator.py
or clear.py

## Clear your environment

To clear your environment, firstly delete the two instances created by create.py if you ran it. Then run the clear.py script.

## Custom the scripts
Into image directory, put an image of your choice, and change
the values in create.py, instance_generator.py and clear.py of the following variables:
- <flavor_name>
- <image_name>
- <image_path>
- <network_name>
- <subnet_name>

*b42agov7*
