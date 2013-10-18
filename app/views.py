from flask import Flask, jsonify, request, abort, make_response, render_template, url_for, redirect
from models import *
from app import db, app
import datetime, requests, json
from pprint import pprint

MASTER_URL = 'http://46.162.89.26:5000/' # API access point for MasterNode
nodelist = []

@app.route('/', methods = ['GET'])
def index():
   return redirect (url_for('get_all_blobs'))

@app.route('/blob/', methods = ['GET'])
def get_all_blobs():
   bl = Blob.query.all()
   path = url_for('get_all_blobs', _external=True)
   # Interate over files to fix displayable values
   for b in bl:
      b.filename = b.file_name()
      b.size = b.file_size()
      b.extension = b.icon_img()
   return render_template("filedisplay.html",
      files = bl,
      download_url = path
   )

@app.route('/blob/', methods =['POST'])
def upload_blob(json=0):
   f = request.files['file']
   fr = f.read()
   b = Blob(item=fr, filename=f.filename, extension=f.content_type, size=len(fr), created_at=datetime.datetime.utcnow(), last_sync=datetime.datetime.utcnow())
   db.session.add(b)
   db.session.commit()
   if json:
      return jsonify ( { 'Blob': b.id} ), 200 
   else:
      return redirect (url_for('get_all_blobs'))

#TODO: Fix this
@app.route('/blob/<int:id>', methods = ['PUT'])
def update_blob(id):
   if request.files['file']:
      b = Blob.query.get(id)
      if b:
         f = request.files['file']
         b.item = f.read()
         b.filename = f.filename
         b.extension = f.content_type
         b.size = len(f.read())
         b.last_sync = datetime.datetime.utcnow()
         db.session.add(b)
         db.session.commit()
         return jsonify ( { 'Blob': b.id } ), 200
      else:
         upload_blob(json=1)

@app.route('/blob/<int:id>/', methods = ['GET'])
def download_blob(id):
   b = Blob.query.get(id)
   response = make_response(b.item)
   response.headers['Content-Type'] = b.extension
   response.headers['Content-Disposition'] = 'attachment; filename="%s"' % b.filename   
   return response

@app.route('/blob/<int:id>/', methods = ['DELETE'])
def delete_blob(id):
   b = Blob.query.get(id)
   db.session.delete(b)
   db.session.commit()
   return jsonify ( {'Deleted blob':id} ), 200

# Register Node with MasterNode
@app.before_first_request
def initialize():
   ipaddr = url_for('index', _external=True)
   payload = {'ip': ipaddr}
   headers = {'content-type': 'application/json'}
   requests.post(MASTER_URL, data=json.dumps(payload), headers=headers)
   update_nodelist()

# Fix the list of nodes in network(excluding self)
def update_nodelist():
   nodeIP = url_for('index', _external=True)
   r = requests.get(MASTER_URL)
   r_json = convert(r.json())
   for i in r_json['Nodes']:
      if not i.get('ipaddr') == nodeIP:
         nodelist.append(i.get('ipaddr'))
 
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
   if method == 'POST':
      url = node+'blob/'
      f = Blob.query.get(fileID)
      files = {'file':(f.filename, f.item)}
      requests.post(url, files=files)

   #TODO: Fix this
   if method == 'PUT':
      url = node+'blob/'+str(fileID)+'/'
      f = Blob.query.get(fileID)
      files = {'file':(f.filename, f.item)}
      requests.put(url, files=files)
           
   if method == 'DELETE':
      url = node+'blob/'+str(fileID)+'/'
      requests.delete(url)


@app.route('/dashboard', methods = ['GET'])
def dashboard():
	return render_template("dashboard.html", 
		nodeIP = url_for('index', _external=True))

