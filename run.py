from app import app, db
import os
basedir = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
   import sys 
   portint=int(sys.argv[-1])
   portstr=str(sys.argv[-1])
   if isinstance(portint, int) and portint < 65535:
      db.create_all()
      app.run('0.0.0.0', port=portint,debug=True)
      try:      
         os.remove(os.path.join(basedir, (portstr + '.db')))
      except OSError:
         pass
