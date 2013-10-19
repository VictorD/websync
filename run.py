from app import app, db
import os, requests, json
from app.utils import add_node, remove_node

if __name__ == '__main__':
   import sys 
   portint=int(sys.argv[-1])
   portstr=str(sys.argv[-1])
   if isinstance(portint, int) and portint < 65535:
      app.config['MASTER_URL'] = 'http://46.162.89.26:5000/' # API access point for MasterNode
      app.config['BASEDIR']    = os.path.abspath(os.path.dirname(__file__))
      
      # Register Node with MasterNode
      headers = {'content-type': 'application/json'}   
      add_node(portstr, headers)

      # Create database
      db.create_all()

      # Run the Node-Server

      app.run('0.0.0.0', use_reloader=False, port=portint,debug=True)

      remove_node()
