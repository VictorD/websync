from app import app
from flask import request
import os, requests, json
from pprint import pprint

def add_node(port, headers):
   payload = {'port': port}
   try:
      masterURL = app.config['master_server_url']
      pprint('Registering node at port ' + port + ' with master at ' + masterURL)
      r = requests.post(masterURL, data=json.dumps(payload), headers=headers)
      r_json = convert(r.json())
      id = r_json.get('Node')
   except ValueError:
      pprint('ERROR: Registration failed. Running in offline mode!')
      id = -1
   app.config['node_id']   = id
   app.config['node_port'] = port

def remove_node():
   try:
      func = request.environ.get('werkzeug.server.shutdown')
      if func is None:
         raise RuntimeError('Not running with the Werkzeug Server')  
      unregisterFromMaster()         
      func()
   except:
      pass
    
def unregisterFromMaster():
   masterURL = app.config['master_server_url']
   pprint("Destroying node...")
   # Remove Node from MasterNode
   id    = app.config['node_id']
   port  = app.config['node_port'] 
   dbdir = app.config['basedir'] 
   if id > 0:
      requests.delete(masterURL + str(id) + ('/'), headers={'content-type': 'application/json'})
      
   # Remove database when server shuts down    
   os.remove(os.path.join(dbdir, (port + '.db')))
   
def createLocalNode(port):
	pprint("Creating local node at port:" + port)
   
# Convert JSON results from unicode to utf-8
# Taken from: http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
