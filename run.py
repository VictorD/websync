from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
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
      add_node(portstr)

      # Create database
      db.create_all()

      # Run the Node-Server
      http_server = HTTPServer(WSGIContainer(app))      
      http_server.listen(portint)
      try:
         IOLoop.instance().start()
      except KeyboardInterrupt:
         IOLoop.instance().stop()
         remove_node()
         print "exited cleanly"
    
