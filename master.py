from app import app
import requests, json, logging

offline_mode = False

def register():
   url  = app.config['MASTER_URL']
   port = app.config['NODE_PORT']

   logging.info('Registering node at port ' + port + ' with master at ' + url)
   try:
      id = request_node_id(url, port)
      app.config['NODE_ID'] = id
      logging.info("Node registered with id: " + id + ", at port: " + port)
   except (ValueError, requests.ConnectionError, requests.Timeout):
      logging.error('ERROR: Master Server not responding. Running in offline mode!')
      global offline_mode
      offline_mode = True
      
def request_node_id(url, port):
      data    = json.dumps({'port': port})
      headers = {'content-type': 'application/json'}   
      r = requests.post(url, data=data, headers=headers, timeout=5)
      id = r.json().get('Node')
      if not isinstance(id, int):
         raise ValueError
      return str(id)

def unregister():
   if is_online():
      logging.info("Unregistering from master server")
      id    = app.config['NODE_ID']
      port  = app.config['NODE_PORT']       
      masterURL = app.config['MASTER_URL']
      requests.delete(masterURL + str(id) + ('/'), headers={'content-type': 'application/json'})

def is_online():
   return (not offline_mode)