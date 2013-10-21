from flask import Flask, jsonify, request, abort, make_response, render_template, url_for, redirect
from models import *
from app import db, app
import datetime, requests, json
from pprint import pprint
from utils import master_update_nodes, master_update_file, shut_down_everything, convert, string_to_timestamp, network_sync
from subprocess import Popen

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
   nodes = []
   try:
      r = requests.get(masterURL, timeout=2)
      r_json = convert(r.json())
      nodes = r_json['Nodes']
   except (requests.Timeout, requests.ConnectionError):
      pass

   return render_template("dashboard.html",
      thisURL   = url_for('index', _external=True),
      masterURL = masterURL,
      nodeList  = nodes)
   
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
   b = received_blob(request)
   db.session.add(b)
   db.session.commit()
   master_update_file('post', b.global_id, b.last_sync)
   if json:
      return jsonify ( { 'Blob': b.global_id} ), 200 
   else:
      return redirect (url_for('index'))

@app.route('/blob/<int:id>/', methods = ['PUT'])
def update_blob(id):
   f = request.files['file']
   if f:
      method = 'put'
      rb = received_blob(request)
      b = Blob.query.get(id)
      if b:
         b.item = rb.item
         b.filename = rb.filename
         b.extension = rb.extension
         b.size = len(rb.item)
         b.last_sync = rb.last_sync
         rb = b
      else:
         method = 'post'
         db.session.add(rb)

      db.session.commit()
      master_update_file(method, rb.global_id, rb.last_sync)
      return jsonify ( { 'Blob': id } ), 200
   else:
      abort(404)

def received_blob(request):
   ts = datetime.datetime.utcnow()
   #if request.files['timestamp']:
   #ts = string_to_timestamp(request.files['timestamp'])

   f  = request.files['file']
   fr = f.read()
   pprint (request.files)
   return Blob(item=fr, filename=f.filename, extension=f.content_type, 
        size=len(fr), created_at = ts, last_sync = ts)


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
   master_update_file('delete', b.global_id, b.last_sync)
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
      
@app.route('/node/createLocal', methods = ['POST'])
def create_local_node():
   port = request.form['port']
   Popen(["python", "run.py", port])
   master_update_nodes()
   return redirect (url_for('index') + "#!/dashboard")

