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
