from app import app
from flask import request
import os, requests, json
from pprint import pprint

def add_node(portStr, headers):
   payload = {'port': portStr}
   try:
      masterURL = app.config['MASTER_URL']
      pprint('Registering node at port ' + portStr + ' with master at ' + masterURL)
      r = requests.post(masterURL, data=json.dumps(payload), headers=headers)
      id = r.json().get('Node')
      if not isinstance(id, int):
         raise ValueError
      pprint('Node registered with ID:' + str(id))
   except ValueError:
      pprint('ERROR: Registration failed. Running in offline mode!')
      id = -1

   idStr = str(id)
   app.config['NODE_ID']   = idStr
   app.config['NODE_PORT'] = portStr
   pprint("Node created with id:" + idStr + ", at port:" + portStr)

def shut_down_everything():  
   try:
      func = request.environ.get('werkzeug.server.shutdown')
      if func:
         func()          
   except:
      pass

def remove_node():
   masterURL = app.config['MASTER_URL']
   
   # Remove Node from MasterNode
   id    = app.config['NODE_ID']
   port  = app.config['NODE_PORT'] 
   dbdir = app.config['BASEDIR'] 
   
   pprint("Destroying node:" + id + ", at port:" + port)
   if int(id) > 0:
      pprint("Unregistering from master server")
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
