from flask import Flask, jsonify, request, abort, make_response
from models import Blob
from app import db, app
import datetime


@app.route('/', methods = ['GET'])
def index():
   return jsonify( {'Welcome':'to this websync thingy'} )

@app.route('/blob/', methods = ['GET'])
def get_all_blogs():
   blob_list = Blob.query.all()
   blob_dict = []
   for b in blob_list:
      blob_dict.append(b.to_dict())
   return jsonify ( {'Blobs':blob_dict} )
   

# Dummy html form to upload files, had issues with curl
@app.route('/upload/', methods = ['GET'])
def test_upload():
   return '''
       <!doctype html>
       <title>Upload new File</title>
       <h1>Upload new File</h1>
       <form action="" method=post enctype=multipart/form-data>
         <p><input type=file name=file>
            <input type=submit value=Upload>
       </form>
       '''


@app.route('/upload/', methods =['POST'])
def upload_blob():
   f = request.files['file']
   fr = f.read()
   b = Blob(item=fr, filename=f.filename, extension=f.content_type, size=len(fr), created_at=datetime.datetime.utcnow(), last_sync=datetime.datetime.utcnow())
   db.session.add(b)
   db.session.commit()
   return jsonify ( {'Blob': b.to_dict()} ), 201

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
      return jsonift ( { 'Blob': b.to_dict() } )

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
