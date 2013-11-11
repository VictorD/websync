#!/usr/bin/env python
from flask import Flask, Blueprint, request, url_for, redirect
from app import db, app, utils
import os, time

from fabric.tasks import execute
from fabric.api import *
from novaclient.v1_1 import client
import novaclient.exceptions


nmod = Blueprint('nova', __name__, url_prefix='/nova')

dash_url = ""

@app.before_first_request
def nmod_init():
   env.warn_only = True
   env.user = 'core'
   env.key_filename = os.path.join(app.config['BASE_DIR'], 'TreasureKey.pem')
   url_for('index') + "#!/dashboard"

@nmod.route('/addInstance', methods = ['POST'])
def add_instance():
   name = request.form.get('instanceName', None)
   if name:
      newInstance = spawnInstance(name)
   return redirect(dash_url)

@nmod.route('/addNode/', methods = ['POST'])
def add_instance_node():
   ip   = request.form.get('ip', None)
   port = request.form.get('port', None)
   if ip:
      execute(remoteWebsyncStart, port, hosts=[ip])
   return redirect(dash_url)
   
@nmod.route('/removeInstance/<instance_id>')
def remove_instance(instance_id):
   try:
      instance = client.servers.get(instance_id)
      instance.delete()
   except novaclient.exceptions.NotFound:
      pass

   ips = client.floating_ips.list()
   oldFLIPs = [x.id for x in ips if x.instance_id == instance_id]
   for flip in oldFLIPs:
      client.floating_ips.delete(flip)

   return redirect(dash_url)

def remoteWebsyncUpdate():
   cmd = "docker build -t=\"websync\" github.com/VictorD/websync"
   run(cmd)
   
def remoteWebsyncStart(port):
   cmd = "docker run -d -p " + port + ":" + port + " websync:latest " + port
   run(cmd)
   
#nova --os-username "student-project-9" --os-tenant-id="b0f27ff1c56b4e18a893157d1cfee705" 
#     --os-auth-url="http://130.240.233.106:5000/v2.0" --os-password="jTKmDEO5Xl5H" image-list
client = client.Client(username   = "student-project-9",
                       project_id = "student-project-9",
                       api_key    = "jTKmDEO5Xl5H",
                       auth_url   = "http://130.240.233.106:5000/v2.0")

def listInstances():
   vm_list = client.servers.list()
   for s in vm_list:
      newIp = getFloatingIP(s)
      if newIp:
         s.ip = newIp
   return vm_list

def getFloatingIP(instance):
   if 'private' in instance.addresses:
      for ip in instance.addresses['private']:

         if ip['OS-EXT-IPS:type'] == 'floating':
            return ip['addr']
   return None

@utils.async
def spawnInstance(instanceName):
  flavors = client.flavors.list()
  images  = client.images.list()
  if flavors and images:
    instance = client.servers.create(name=instanceName, image=images[0], flavor=flavors[0], key_name="TreasureKey")
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
    ip = assignFloatingIP(instance)
    if ip:
      time.sleep(20) # Give server time to boot
      execute(remoteWebsyncUpdate, hosts=[ip])
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
