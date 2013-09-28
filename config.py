import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')

