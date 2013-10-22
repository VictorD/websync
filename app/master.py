from utils import JSON_HEADER, timestamp_to_string, convert
import requests, json, logging

OFFLINE_MODE = False
URL = ""
NODE_ID = "0"
NODE_URL = ""
NODE_PORT = "0"
NODE_LIST = []

def set_node_url(nu):
   global NODE_URL
   NODE_URL = nu

def register(url, port):
   global URL, NODE_ID, OFFLINE_MODE, NODE_PORT
   URL = url
   NODE_PORT = port
   logging.info('Registering node at port ' + port + ' with master at ' + url)
   try:
      NODE_ID = request_node_id(url, port)
      logging.info("Node received ID: " + NODE_ID)
   except (ValueError, requests.ConnectionError, requests.Timeout):
      OFFLINE_MODE = True
      logging.error('ERROR: Registration failed. Node running in offline mode!')
   return NODE_ID
      
def request_node_id(url, port):
      data = json.dumps({'port': port})
      r = requests.post(url, data=data, headers=JSON_HEADER, timeout=10)
      id = r.json().get('Node')
      if isinstance(id, int):
         return str(id)
      else:
         raise ValueError

def unregister():
   if is_online():
      logging.info("Unregistering from master server")
      requests.delete(URL + NODE_ID + ('/'), headers=JSON_HEADER)
      
def is_online():
   return (not OFFLINE_MODE)

def get_nodes():
   if is_online():
      logging.info("Updating node list")
      update_nodes()
   logging.info(NODE_LIST)
   return NODE_LIST

# Fix the list of nodes in network(excluding self)
def update_nodes():
   global NODE_LIST
   if is_online():
      try:
         r = requests.get(URL, timeout=30)
         r_json = convert(r.json())
         NODE_LIST = []
         for i in r_json['Nodes']:
            if not i.get('ipaddr') == NODE_URL:
               NODE_LIST.append(i)
         logging.info("Updated Node list. Found " + str(len(NODE_LIST)) + " nodes")
      except (requests.Timeout, requests.ConnectionError):
         logging.error("Failed to retrieve Node list from Master Node")

# Method used to inform MasterNode about changes in files
def update_file(method, fileID, timestamp):
   if is_online():
      logging.info("Informing MasterServer of File update: " + str(fileID))
      ts = timestamp_to_string(timestamp)
      js = {'timestamp': ts, 'fileid': fileID, 'port': NODE_PORT}
      requests.post(URL + method + '/', data=json.dumps(js), headers=JSON_HEADER)