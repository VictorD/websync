from app import app
from models import Blob
from flask import request, url_for
import os, requests, json, logging, datetime
from subprocess import call

JSON_HEADER = {'content-type': 'application/json'}   
   
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
         requests.post(url, files=file, data=values)
      elif method == 'PUT':
         requests.put(url + str(fileID) + '/', files=file, data=values)
      elif method == 'DELETE':
         requests.delete(url + str(fileID) + '/')

def timestamp_to_string(timestamp):
   return timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')

def string_to_timestamp(timeStr):
  return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S.%f')
  
def current_time():
   return datetime.datetime.utcnow()

