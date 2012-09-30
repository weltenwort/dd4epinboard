# -*- encoding:utf-8 -*-
import datetime

#from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import validates

from ..db import db
from .entry import entry_types


class Pinboard(db.Model):
    __bind_key__ = "users"
    __tablename__ = "pinboard"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(200))
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.now)
    description = db.Column(db.UnicodeText)
    public = db.Column(db.Boolean, default=False)

    #current_version_id = db.Column(db.Integer, db.ForeignKey("pinboard_version.id"))
    #current_version = db.relationship("PinboardVersion", uselist=False)

    owner_username = db.Column(db.Unicode(200), db.ForeignKey("user.username"))
    owner = db.relationship("User",
            backref=db.backref("owned_pinboards",
                cascade="all, delete-orphan",
                single_parent=True,
                ))

    def add_entry(self, entry_type, entry_id):
        if PinboardEntry.query.filter(
                PinboardEntry.pinboard == self,
                PinboardEntry.entry_type == entry_type,
                PinboardEntry.entry_id == entry_id,
                ).count() == 0:
            self.entries.append(PinboardEntry(
                entry_type=entry_type,
                entry_id=entry_id,
                ))
        else:
            raise self.EntryAlreadyPresentError("The entry ({}, {}) is already in this pinboard.".format(
                entry_type, entry_id,
                ))

    def remove_entry(self, entry_type, entry_id):
        entry = PinboardEntry.query.filter(
                PinboardEntry.pinboard == self,
                PinboardEntry.entry_type == entry_type,
                PinboardEntry.entry_id == entry_id,
                ).first()
        if entry is not None:
            db.session.delete(entry)
        else:
            raise self.EntryNotPresentError("The entry ({}, {}) is not in this pinboard.".format(
                entry_type, entry_id,
                ))

    def as_dict(self, full=False):
        return dict(
                id=self.id,
                name=self.name,
                description=self.description,
                public=self.public,
                owner_username=self.owner_username,
                entries=[e.as_dict(full=full) for e in self.entries],
                )

    class EntryAlreadyPresentError(ValueError):
        pass

    class EntryNotPresentError(ValueError):
        pass


#class PinboardVersion(db.Model):
    #__bind_key__ = "users"
    #__tablename__ = "pinboard_version"

    #id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.Unicode(200))
    #timestamp = db.Column(db.DateTime(), default=datetime.datetime.now)
    #description = db.Column(db.UnicodeText)

    #pinboard_id = db.Column(db.Integer, db.ForeignKey("pinboard.id"))
    #pinboard = db.relationship("Pinboard",
            #backref=db.backref("versions",
                #cascade="all, delete-orphan",
                #order_by=timestamp,
                #single_parent=True,
                #))


class PinboardEntry(db.Model):
    __bind_key__ = "users"
    __tablename__ = "pinboard_entry"

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    entry_id = db.Column(db.Integer, nullable=False)
    entry_type = db.Column(db.Unicode(200), nullable=False)

    pinboard_id = db.Column(db.Integer, db.ForeignKey("pinboard.id"))
    pinboard = db.relationship("Pinboard",
            backref=db.backref("entries",
                cascade="all, delete-orphan",
                collection_class=ordering_list("position"),
                single_parent=True,
                ))

    #pinboard_version_id = db.Column(db.Integer, db.ForeignKey("pinboard_version.id"))
    #pinboard_version = db.relationship("PinboardVersion",
            #backref=db.backref("entries",
                #cascade="all, delete-orphan",
                #collection_class=ordering_list("position"),
                #single_parent=True,
                #))

    @validates("entry_type")
    def validate_entry_type(self, key, entry_type):
        if entry_type in entry_types:
            return entry_type
        else:
            raise ValueError("Unkown entry type: {}".format(entry_type))

    def as_dict(self, full=False):
        if full:
            entry = entry_types[self.entry_type].query.get(self.entry_id)
            return entry.as_dict()
        else:
            return dict(
                    id=self.entry_id,
                    entry_type=self.entry_type,
                    )
