#!/usr/bin/env python
from fabric.api import *
from fabric.tasks import execute
from novaclient.v1_1 import client
import os, time

class FabricSupport:
    def __init__ (self):
        pass

    def run(self, host, port, command):
        env.host_string = "%s:%s" % (host, port)
        run(command)

myfab = FabricSupport()
#myfab.run('example.com', 22, 'uname')

#nova --os-username "student-project-9" --os-tenant-id="b0f27ff1c56b4e18a893157d1cfee705" 
#     --os-auth-url="http://130.240.233.106:5000/v2.0" --os-password="jTKmDEO5Xl5H" image-list
def createClient():
   return client.Client(username   = "student-project-9",
                        project_id = "student-project-9",
                        api_key    = "jTKmDEO5Xl5H",
                        auth_url   = "http://130.240.233.106:5000/v2.0")
                   
def spawnInstance(c):
   flavors = c.flavors.list()
   images  = c.images.list()
   if flavors and images:
      instance = c.servers.create(name="Meepo", image=images[0], flavor=flavors[0], key_name="TreasureKey")

      status = instance.status

      print "status: %s" % status
      while status != 'ACTIVE':
         time.sleep(2)
         print "."
         # Update status fields
         instance = c.servers.get(instance.id)
         status = instance.status

      print "status: %s" % status

      # Wait a little to ensure we got a fixed ip (To prevent error: nw_cache missing)
      time.sleep(1)
   return instance

def assignFloatingIP(client, instance):
        ips = client.floating_ips.list()
        new_floating_ip = client.floating_ips.create()
        instance.add_floating_ip(new_floating_ip)
        serverIP = str(new_floating_ip.ip)
        print "Server IP: " + serverIP
        return serverIP

def setupDocker(ip):
   env.key_filename = '/home/vcd/code/websync/TreasureKey.pem'
   env.user = 'core'
   env.host_string = ip + ":22"
   run('uname -a')

if __name__ == '__main__':
    client   = createClient()
    instance = spawnInstance(client)
    if instance:
      serverIP = assignFloatingIP(client, instance)
      time.sleep(2)
      if serverIP:
         setupDocker(serverIP)

