from app import app
from models import Blob
from flask import request, url_for
import os, requests, json, logging
from pprint import pprint
from subprocess import call

nodelist = []

def add_node():
   port = app.config['NODE_PORT']
   masterURL = app.config['MASTER_URL']
   pprint('Registering node at port ' + port + ' with master at ' + masterURL)
   try:
      data    = {'port': port}
      headers = {'content-type': 'application/json'}   
      regResponse = requests.post(masterURL, data=json.dumps(data), headers=headers, timeout=2)
      id = get_registration_id(regResponse)
   except (ValueError, requests.ConnectionError, requests.Timeout):
      pprint('ERROR: Master Server not responding. Running in offline mode!')
      id = "-1"

   app.config['NODE_ID']   = id
   pprint("Node created with id:" + id + ", at port:" + str(port))

def get_registration_id(r):
      id = r.json().get('Node')
      if not isinstance(id, int):
         raise ValueError
      return str(id)

def remove_node():
   masterURL = app.config['MASTER_URL']
   
   # Remove Node from MasterNode
   id    = app.config['NODE_ID']
   port  = app.config['NODE_PORT'] 
   dbdir = app.config['BASEDIR'] 
   
   pprint("Destroying node:" + id + ", at port:" + port)
   if int(id) > 0:
      pprint("Unregistering from master server")
      requests.delete(masterURL + str(id) + ('/'), headers={'content-type': 'application/json'}, timeout=1)
      
   # Remove database when server shuts down    
   os.remove(os.path.join(dbdir, (port + '.db')))
   
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
        
# Fix the list of nodes in network(excluding self)
def master_update_nodes():
   id = app.config['NODE_ID']
   if int(id) > 0:
      masterURL = app.config['MASTER_URL']   
      nodeIP    = url_for('index', _external=True)
      r = requests.get(masterURL)
      r_json = convert(r.json())
      global nodelist
      nodelist = []
      for i in r_json['Nodes']:
         if not i.get('ipaddr') == nodeIP:
            nodelist.append(i.get('ipaddr'))

# This methods handles communication between nodes
# PARAMS: (str , int, str) -> REST method -> Which File -> Destination Node
def network_sync(method, fileID, node):
   logging.info("Querying file with ID: " + str(fileID))
   f = Blob.query.get(fileID)
   if f:
      method = method.upper()
      url    = node + '/blob/'
      logging.info("File found! Sending to " + url)
      
      file = {'file':(f.filename, f.item)}
      values = {'timestamp': str(f.last_sync) }
      
      if method == 'POST':        
         r = requests.post(url, files=file, data=values)
      elif method == 'PUT':
         logging.info("Sending PUT request to " + url)
         requests.put(url + str(fileID) + '/', files=files, data=data)
      elif method == 'DELETE':
         requests.delete(url + str(fileID) + '/')

# Method used to inform masternode about changes in files
def master_update_file(method, fileID, timestamp):
   id = app.config['NODE_ID']
   if int(id) > 0:
      masterURL = app.config['MASTER_URL']
      port = app.config['NODE_PORT']
      ts = timestamp_to_string(timestamp)
      js = {'timestamp': ts, 'fileid': fileID, 'port': port}
      requests.post((masterURL + method + '/'), data=json.dumps(js), headers = {'content-type': 'application/json'})

def timestamp_to_string(timestamp):
   return timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')

def string_to_timestamp(timeStr):
  return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S.%f')

