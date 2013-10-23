import requests, json, logging, server, master
from flask import Flask, jsonify, request, abort, make_response, render_template, url_for, redirect
from models import *
from app import db, app
from utils import convert, string_to_timestamp, network_sync, current_time
from subprocess import Popen

# Register Node with MasterNode
@app.before_first_request
def initialize():
   url = url_for('index', _external=True)
   master.set_node_url(url)
   master.update_nodes()

@app.route('/')
def index():
	return render_template("index.html")
   
@app.route('/offlineMode/<int:off>')
def offlineMode(off):
   master.set_offline_mode(off)
   return jsonify ( { 'OfflineMode': not master.is_online() } ), 200
   
@app.route('/reconnect/')
def reconnect():
   master.register_node()
   return jsonify ( { 'Online': master.is_online() } ), 200

@app.route('/logs/')   
@app.route('/logs/<int:max>')
def logtext(max=50):
   log_dir = app.config['BASE_DIR'] 
   file = open(log_dir + "/websync.log", 'r')
   log_lines = [line for line in file.readlines()]
   log_lines = log_lines[-max:] # truncate to <max> lines
   return render_template("log.html", lines = reversed(log_lines)) # show newest first
	
@app.route('/dashboard/', methods = ['GET'])
def dashboard():
   return render_template("dashboard.html",
      thisURL     = url_for('index', _external=True),
      masterURL   = master.URL,
      node_list   = master.get_nodes(),
      node_online = master.is_online())
   
@app.route('/selfdestruct', methods=['GET'])
def shutdown():
    server.stop()
    return "<h3>Shutting down server...</h3>"
		
@app.route('/blob/', methods = ['GET'])
def get_all_blobs():
   bl = Blob.query.all()
   path = url_for('get_all_blobs', _external=True)
   # Interate over files to fix displayable values
   for b in bl:
      b.filename = b.file_name()
      b.size = b.file_size()
      b.is_image = (b.extension == 'image/jpeg' or b.extension == 'image/png')
      b.extension = b.icon_img()
   return render_template("filedisplay.html",
      files = bl,
      download_url = path
   )

@app.route('/blob/',          methods = ['POST', 'PUT'])
@app.route('/blob/<int:id>/', methods = ['POST', 'PUT'])
def update_blob(id=None):
   logging.info("Received BLOB Update")
   rb = blob_from_request(request)

   b  = None
   if rb.global_id:
      b = Blob.query.filter_by(global_id=rb.global_id).first()
   elif id:
      b = Blob.query.get(id)

   method = 'post'
   if b:
      # update an existing blob
      method = 'put'
      b.item      = rb.item
      b.filename  = rb.filename
      b.extension = rb.extension
      b.size      = len(rb.item)
      b.last_sync = rb.last_sync
   else:
      # add new blob
      b = rb
      db.session.add(b)
      logging.info("Added new Blob with id: " + str(b.global_id))
   
   if not b.global_id:
         b.global_id = get_next_global_id()

   db.session.commit()      
   master.update_file(method, b.global_id, b.last_sync)

   return jsonify ( { 'Blob': b.id } ), 200

def blob_from_request(r):
   f  = r.files['file']
   fr = f.read()
   ts = current_time()
   rb = Blob(item=fr, filename=f.filename, extension=f.content_type, 
             size=len(fr), created_at = ts, last_sync = ts)
   logging.info(r.form)
   if r.form:
      if r.form['timestamp']:
         rb.last_sync = string_to_timestamp(r.form['timestamp'])
      if r.form['global_id']:
         rb.global_id = r.form['global_id']
   return rb
        
def get_next_global_id():
   gid = 0
   if master.is_online():   
      try:
         r = requests.get(master.URL + "next/", timeout=30)
         r_json = convert(r.json())
         gid = int(r_json['nextID'])
         logging.info('Global id received: ' + str(gid))
      except (requests.Timeout, requests.ConnectionError):
         logging.error('Global ID request timeout. Using default value')
   return gid

@app.route('/blob/<int:id>/', methods = ['GET'])
def download_blob(id):
   b = Blob.query.get(id)
   response = make_response(b.item)
   response.headers['Content-Type'] = b.extension
   response.headers['Content-Disposition'] = 'attachment; filename="%s"' % b.filename   
   return response

@app.route('/blob/<int:id>/', methods = ['DELETE'])
def delete_blob(id):
   if request.json and request.json['global_id']:
      b = Blob.query.filter_by(global_id = request.form['global_id']).first()
   else:
      b = Blob.query.get(id)
      
   db.session.delete(b)
   db.session.commit()
   master.update_file('delete', b.global_id, b.last_sync)
   return jsonify ( {'Deleted blob':id} ), 200

# MasterNodes API endpoint
@app.route('/mn/', methods = ['GET'])
def master_orders():
   logging.info("Received MN request")
   if request.json and 'nodeurl' in request.json and 'method' in request.json and 'fileid' in request.json:
      n = request.json['nodeurl']
      f = request.json['fileid']      
      m = request.json['method']
      logging.info("Performing network sync")
      network_sync(m, f, n)
      return jsonify ({ 'Node':n, 'File':f ,'Method':m }), 200
   else:
      abort(404)
      
@app.route('/node/createLocal', methods = ['POST'])
def create_local_node():
   port = request.form['port']
   Popen(["python", "run.py", port])
   master.update_nodes()
   return redirect (url_for('index') + "#!/dashboard")

