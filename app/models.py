from app import db

class Blob(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   filename = db.Column(db.String(50))
   extension = db.Column(db.String(20))
   size = db.Column(db.Integer)
   item = db.Column(db.Binary)
   created_at = db.Column(db.DateTime)
   last_sync = db.Column(db.DateTime)

   def to_dict(self):
      return dict(
         id = self.id,
         filename = self.filename,
         extension = self.extension,
         size = self.size,
         created_at = self.created_at,
         last_sync = self.last_sync
      )

   def __repr__(self):
      return '<Blob %r>' % (self.id)

   def icon_img(self):
      i = self.extension.split("/")[-1]

      # Documents
   
      if i == "plain":
         i = "/static/img/txt.png"

      elif i == "pdf":
         i = "/static/img/pdf.png"
     
      # Images

      elif i == "gif":
         i = "/static/img/gif.png"

      elif i == "jpeg":
         i = "/static/img/jpg.png"


      elif i == "png":
         i = "/static/img/png.png" 
      
      # Programming      
      elif i == "x-python":
         i = "/static/img/py.png"

      elif i == "x-csrc":
         i = "/static/img/c.png"
      
      elif i == "css":
         i = "/static/img/css.png"

      elif i == "html":
         i = "/static/img/html.png"

      # Others

      else:
         i = "/static/img/_blank.png"

      return i

   def file_size(self):
      if self.size > 1000000:
         return "%s MB" % (self.size/1000000)
      elif self.size > 1000:
         return "%s KB" % (self.size/1000)
      else:
         return "%s B" % (self.size)

   def file_name(self):
      return str(self.filename.rsplit(".",1)[0])
