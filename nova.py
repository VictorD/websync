#!/usr/bin/env python
from fabric.api import *
from novaclient.v1_1 import client
import os, time

#nova --os-username "student-project-9" --os-tenant-id="b0f27ff1c56b4e18a893157d1cfee705" 
#     --os-auth-url="http://130.240.233.106:5000/v2.0" --os-password="jTKmDEO5Xl5H" image-list

def createServer():
    nv = client.Client(username="student-project-9",
                   api_key="jTKmDEO5Xl5H",
                   project_id="student-project-9", 
                   auth_url="http://130.240.233.106:5000/v2.0")

    flavors = nv.flavors.list()
    images = nv.images.list()
    instance = nv.servers.create(name="Meepo", 
                    image=images[0], flavor=flavors[0], key_name="TreasureKey")

    status = instance.status

    print "status: %s" % status
    while status == 'BUILD':
        time.sleep(2)
        print "."
        # Update status fields
        instance = nv.servers.get(instance.id)
        status = instance.status
	print "status: %s" % status

	ips = nv.floating_ips.list()

	new_floating_ip = nv.floating_ips.create()
	instance.add_floating_ip(new_floating_ip)

	env.hosts = [new_floating_ip.ip]
	env.user = 'core'
	env.key_filename = '/home/vcd/code/websync/TreasureKey.pem'
	run('uname -a')

if __name__ == '__main__':
	createServer()
