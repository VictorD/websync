#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import app, db
import os, requests, json, logging
import server
import app.utils as utils
from werkzeug.debug import DebuggedApplication

if __name__ == '__main__':
   app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
   
   app.config['MASTER_URL'] = 'http://46.162.89.26:5000/' # API access point for MasterNode
   app.config['BASEDIR']    = os.path.abspath(os.path.dirname(__file__))
   import sys 
   portint=int(sys.argv[-1])
   portstr=str(sys.argv[-1])
   if isinstance(portint, int) and portint < 65535:
      app.config['NODE_PORT'] = portstr
      
      # Create database
      db.create_all()

      # Register Node with MasterNode
      utils.add_node()

      # Start the app in Tornado
      server.start(app, portint)
      #app.run(host='0.0.0.0', use_reloader=False, port=portint, debug=True)
      
      # Unregister
      utils.remove_node()

      logging.info('Exited successfully')