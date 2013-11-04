#!/usr/bin/env python	
from novaclient.v1_1 import client
import os, time

#nova --os-username "student-project-9" --os-tenant-id="b0f27ff1c56b4e18a893157d1cfee705" 
#     --os-auth-url="http://130.240.233.106:5000/v2.0" --os-password="jTKmDEO5Xl5H" image-list
client = client.Client(username   = "student-project-9",
                       project_id = "student-project-9",
                       api_key    = "jTKmDEO5Xl5H",
                       auth_url   = "http://130.240.233.106:5000/v2.0")

def spawnInstance():
  flavors = client.flavors.list()
  images  = client.images.list()
  if flavors and images:
    instance = client.servers.create(name="Meepo", image=images[0], flavor=flavors[0], key_name="TreasureKey")
    status   = instance.status

    print "status: %s" % status
    while status != 'ACTIVE':
        time.sleep(2)
        print "."
        # Update status fields
        instance = client.servers.get(instance.id)
        status = instance.status

    print "status: %s" % status

    # Wait a little to ensure we got a fixed ip (To prevent error: nw_cache missing)
    time.sleep(2)
  return instance
   
#def destroyInstance():

def assignFloatingIP(instance):
        ips = client.floating_ips.list()
        new_floating_ip = client.floating_ips.create()
        instance.add_floating_ip(new_floating_ip)
        time.sleep(1)
        serverIP = str(new_floating_ip.ip)
        print "Server IP: " + serverIP
        return serverIP
