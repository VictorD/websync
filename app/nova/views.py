#!/usr/bin/env python
from flask import Flask, Blueprint, request, url_for, redirect
from app import db, app, utils
from novaclient.v1_1 import client
import novaclient.exceptions
import os, time
from pprint import pprint 

nmod = Blueprint('nova', __name__, url_prefix='/nova')

dash_url = ""

@app.before_first_request
def nmod_init():
   url_for('index') + "#!/dashboard"

@nmod.route('/addInstance', methods = ['POST'])
def add_instance():
   server_id = 0

   if request.form and 'instanceName' in request.form:
      name = request.form['instanceName']
      newInstance = spawnInstance(name)

   return redirect(dash_url)

@nmod.route('/removeInstance/<server_id>')
def remove_instance(server_id):
   try:
      instance = client.servers.get(server_id)
      instance.delete()
   except novaclient.exceptions.NotFound:
      pass

   return redirect(dash_url)

@nmod.route('/addNode/<id>', methods = ['POST'])
def add_instance_node():
   return port

   
#nova --os-username "student-project-9" --os-tenant-id="b0f27ff1c56b4e18a893157d1cfee705" 
#     --os-auth-url="http://130.240.233.106:5000/v2.0" --os-password="jTKmDEO5Xl5H" image-list
client = client.Client(username   = "student-project-9",
                       project_id = "student-project-9",
                       api_key    = "jTKmDEO5Xl5H",
                       auth_url   = "http://130.240.233.106:5000/v2.0")

def listInstances():
   vm_list = client.servers.list()
   for v in vm_list:
      addr = v.addresses
      if 'private' in v.addresses:
         for ip in v.addresses['private']:
            if ip['OS-EXT-IPS:type'] == 'floating':
               v.ip = ip['addr']
   return vm_list

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
    assignFloatingIP(instance)
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
