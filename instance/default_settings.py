# -*- encoding:utf-8 -*-
import os

base_path = os.path.dirname(__file__)

DEBUG = False
ASSETS_DEBUG = False
ASSETS_CACHE = False
ASSETS_MANIFEST = "file"
ASSETS_AUTO_BUILD = False
SQLALCHEMY_DATABASE_URI = "sqlite:////{}/data.db".format(base_path)
SQLALCHEMY_BINDS = {
        "users": "sqlite:////{}/users.db".format(base_path),
        }
SECRET_KEY = 'your-custom-secret'
OBJECTS_PER_PAGE = 10
SERVER_NAME = "pinboard2.weltenwort.de"
LOG_FILENAME = "pinboard.log"
