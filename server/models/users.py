# -*- encoding:utf-8 -*-
import datetime
import hashlib
import os

#from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
#from sqlalchemy.orm import validates

from ..db import db
#from .entry import entry_types


class User(db.Model, UserMixin):
    __bind_key__ = "users"

    username = db.Column(db.Unicode(200), primary_key=True)
    _password = db.Column("password", db.String(128))
    admin = db.Column(db.Boolean, default=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def set_password(self, password):
        h = hashlib.sha256()
        h.update(os.urandom(256))
        salt = h.hexdigest()
        self._password = salt + self._hash_password(password, salt=salt)

    @property
    def salt(self):
        return self._password[:64]

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = self.salt
        h = hashlib.sha256()
        h.update(salt)
        h.update(password)
        return h.hexdigest()

    def check_password(self, password):
        return self.salt + self._hash_password(password) == self._password

    def get_id(self):
        return self.username


#class EntryAssociation(db.Model):
    #__bind_key__ = "users"

    #id = db.Column(db.Integer(), primary_key=True)
    #creation_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    #entry_id = db.Column(db.Integer, nullable=False)
    #entry_type = db.Column(db.Unicode(200), nullable=False)

    #username = db.Column(db.Unicode(200), db.ForeignKey("user.username"))
    #user = db.relationship("User",
            #backref=db.backref("entries", order_by=creation_date),
            #)

    #@validates("entry_type")
    #def validate_entry_type(self, key, entry_type):
        #if entry_type in entry_types:
            #return entry_type
        #else:
            #raise ValueError("Unkown entry type: {}".format(entry_type))
