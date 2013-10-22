#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import app, db
import os, requests, json, logging
import server, master

def initLogger():
   # Log to console and websync.log
   logging.basicConfig(
      format='%(asctime)s %(message)s', 
      datefmt='%Y-%m-%d %H:%M:%S: ', 
      filename='websync.log', 
      level=logging.INFO)

   console = logging.StreamHandler()
   console.setLevel(logging.INFO)
   logging.getLogger().addHandler(console)

if __name__ == '__main__':
   initLogger()
   import sys 
   portint=int(sys.argv[-1])
   portstr=str(sys.argv[-1])
   if isinstance(portint, int) and portint < 65535:
      app.config['MASTER_URL'] = 'http://46.162.89.26:5000/' # API access point for MasterNode
      app.config['NODE_PORT']  = portstr
      app.config['BASE_DIR']   = os.path.abspath(os.path.dirname(__file__))
      
      # Create database
      db.create_all()

      master.register()
      server.start(app, portint)
      master.unregister()
      
      # Remove database when server shuts down    
      os.remove(os.path.join(app.config['BASE_DIR'], (portstr + '.db')))
      logging.info('Exited successfully')
