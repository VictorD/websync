#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, logging, server
from app import app, db, master

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
      app.config['BASE_DIR']   = os.path.abspath(os.path.dirname(__file__))
      
      # API access point for MasterNode
      master.register("http://130.240.95.35:5000/", portstr)

      # Create database
      db.create_all()

      server.start(app, portint)
      
      # Remove database when server shuts down    
      os.remove(os.path.join(app.config['BASE_DIR'], (portstr + '.db')))
      
      master.unregister()      
      logging.info('Exited successfully')
