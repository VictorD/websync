import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))

portdb=str(sys.argv[-1])

DEBUG = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, (portdb + '.db'))
