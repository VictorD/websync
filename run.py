from app import app, db

if __name__ == '__main__':
   import sys 
   port=int(sys.argv[-1])
   if isinstance(port, int):
      db.create_all()
      app.run('0.0.0.0', port=port,debug=True)
