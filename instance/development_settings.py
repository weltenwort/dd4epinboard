# -*- encoding:utf-8 -*-
DEBUG = True
ASSETS_AUTO_BUILD = True
SQLALCHEMY_DATABASE_URI = "sqlite:////home/laeroth/tmp/data.db"
SQLALCHEMY_BINDS = {
        "users": "sqlite:////home/laeroth/tmp/users.db",
        }
SERVER_NAME = None
