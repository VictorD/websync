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
    if flavors and images:
        instance = nv.servers.create(name="Meepo", image=images[0], flavor=flavors[0], key_name="TreasureKey")

        status = instance.status

        print "status: %s" % status
        while status != 'ACTIVE':
            time.sleep(2)
            print "."
            # Update status fields
            instance = nv.servers.get(instance.id)
            status = instance.status
	    print "status: %s" % status

        #while not nv.fixed_ips.list():
        #    time.sleep(1)
        #    print "waiting for fixed ip"
        time.sleep(2)
        ips = nv.floating_ips.list()

        new_floating_ip = nv.floating_ips.create()
        instance.add_floating_ip(new_floating_ip)
    
        env.roledefs = {
            'coreos' : ['core@' + str(new_floating_ip.ip)]
        }
        env.key_filename = '/home/vcd/code/websync/TreasureKey.pem'
        print env.hosts

@roles('coreos')
def deploy():
	run('uname -a')

if __name__ == '__main__':
    createServer()
    deploy()

