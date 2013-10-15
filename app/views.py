from flask import Flask, jsonify, request, abort, make_response, render_template, url_for, redirect
from models import *
from app import db, app
import datetime, requests, json
from pprint import pprint


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
def upload_blob():
   f = request.files['file']
   fr = f.read()
   b = Blob(item=fr, filename=f.filename, extension=f.content_type, size=len(fr), created_at=datetime.datetime.utcnow(), last_sync=datetime.datetime.utcnow())
   db.session.add(b)
   db.session.commit()
   return redirect (url_for('get_all_blobs'))

@app.route('/blob/<int:id>', methods = ['PUT'])
def update_blob(id):
   if request.files['file']:
      b = Blob.query.get(id)
      f = request.files['file']
      b.item = f.read()
      b.filename = f.filename
      b.extension = f.content_type
      b.size = len(f.read())
      b.last_sync = datetime.datetime.utcnow()
      db.session.add(b)
      db.session.commit()
      return jsonify ( { 'Blob': b.to_dict() } )

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
   return jsonify ( {'Deleted blob':id} )

# Register Node with MasterNode
@app.before_first_request
def initialize():
   url = 'http://46.162.89.26:5000/' # IP for MasterNode server
   ipaddr = ip_converter(url_for('index', _external=True))
   payload = {'ip': ipaddr}
   headers = {'content-type': 'application/json'}
   r = requests.post(url, data=json.dumps(payload), headers=headers)
   return ""

def ip_converter(server_url):
   return str(server_url.split("/")[-2])

