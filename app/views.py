from flask import Flask, jsonify, request, abort, make_response, render_template, url_for, redirect
from models import *
from app import db, app
import datetime, requests, json
from pprint import pprint
from utils import master_update_nodes, master_update_file, shut_down_everything, convert

# Register Node with MasterNode
@app.before_first_request
def initialize():
   master_update_nodes()

@app.route('/', methods = ['GET'])
def index():
	return render_template("index.html")
	
@app.route('/dashboard/', methods = ['GET'])
def dashboard():
   masterURL = app.config['MASTER_URL']
   r = requests.get(masterURL)
   r_json = convert(r.json())
   return render_template("dashboard.html",
      thisURL   = url_for('index', _external=True),
      masterURL = masterURL,
      nodeList  = r_json['Nodes'])
   
@app.route('/selfdestruct', methods=['GET'])
def shutdown():
    shut_down_everything()
    return 'Server is shutting down...'
		
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
   master_update_file('post', b.id, b.last_sync)
   if json:
      return jsonify ( { 'Blob': b.id} ), 200 
   else:
      return redirect (url_for('index'))

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
   updateMaster('delete', b.id, b.last_sync)
   return jsonify ( {'Deleted blob':id} ), 200

# MasterNodes API endpoint
@app.route('/mn/', methods = ['GET'])
def masterOrders():
   if request.json and 'nodeurl' in request.json and 'method' in request.json and 'fileid' in request.json:
      n = request.json['nodeurl']
      f = request.json['fileid']      
      m = request.json['method']
      network_sync(m, f, n)
      return jsonify ({ 'Node':n, 'File':f ,'Method':m }), 200
   else:
      abort(404)

