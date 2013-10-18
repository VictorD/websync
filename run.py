from app import app, db
import os, requests, json
basedir = os.path.abspath(os.path.dirname(__file__))
from app.views import MASTER_URL, convert

if __name__ == '__main__':
   import sys 
   portint=int(sys.argv[-1])
   portstr=str(sys.argv[-1])
   if isinstance(portint, int) and portint < 65535:
      # Register Node with MasterNode
      payload= {'port': portstr}
      headers = {'content-type': 'application/json'}
      r = requests.post(MASTER_URL, data=json.dumps(payload), headers=headers)
     
      # Create database
      db.create_all()

      # Run the Node-Server
      app.run('0.0.0.0', use_reloader=False, port=portint,debug=True)

      # Remove Node from MasterNode
      r_json = convert(r.json())
      i = r_json.get('Node')
      requests.delete(MASTER_URL+str(i)+('/'), headers={'content-type': 'application/json'})
      
      # Remove database when server shuts down    
      os.remove(os.path.join(basedir, (portstr + '.db')))
