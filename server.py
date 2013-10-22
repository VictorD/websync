#import master
import tornado.ioloop
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.options import options
import signal, logging

is_closing = False
       
def start(app, port=5000):   
   tornado.options.parse_command_line()
   http_server = HTTPServer(WSGIContainer(app))      
   http_server.listen(port)
   signal.signal(signal.SIGINT, signal_handler)
   tornado.ioloop.PeriodicCallback(try_exit, 100).start()
   tornado.ioloop.IOLoop.instance().start()

# Poll every 100 ms to see if server should stop
def try_exit(): 
    global is_closing
    if is_closing:
        tornado.ioloop.IOLoop.instance().stop()

def signal_handler(signum, frame):
   stop()

def stop():
   global is_closing
   is_closing = True
   