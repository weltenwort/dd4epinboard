# -*- encoding:utf-8 -*-
import json

#from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import TypeDecorator, UnicodeText
from sqlalchemy import func

from ..db import db


class JsonType(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = unicode(json.dumps(value))

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Entry(object):
    __bind_key__ = None

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(200))
    text = db.Column(db.UnicodeText())
    data = db.Column(JsonType())

    filter_col_names = []

    @staticmethod
    def _split_text(data):
        text = data.get("text", "")
        try:
            del data["text"]
        except KeyError:
            pass
        return data, text

    @classmethod
    def get_filter_options(cls):
        filter_options = dict()

        for filter_col_name in cls.filter_col_names:
            filter_attr = getattr(cls, filter_col_name)
            filter_options[filter_col_name] = dict((key, value) for key, value in\
                    db.session.query(filter_attr, func.count(filter_attr)).group_by(filter_attr).all()
                    if key is not None and key != ""
                    )

        return filter_options

    def as_dict(self):
        return self.data


class Deity(db.Model, Entry):
    __tablename__ = "deity"

    alignment = db.Column(db.Unicode(200))

    filter_col_names = ["alignment", ]

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                alignment=data.get("alignment"),
                data=data,
                )

    def as_dict(self):
        return dict(
                entry_type="deity",
                id=self.id,
                name=self.name,
                alignment=self.alignment,
                )


class Feat(db.Model, Entry):
    __tablename__ = "feat"

    tier = db.Column(db.Unicode(200))
    prerequisite = db.Column(db.Unicode(200))

    filter_col_names = ["tier", ]

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                tier=data.get("tiername"),
                prerequisite=data.get("prerequisite"),
                data=data,
                )

    def as_dict(self):
        return dict(
                entry_type="feat",
                id=self.id,
                name=self.name,
                tier=self.tier,
                prerequisite=self.prerequisite,
                )


class Class(db.Model, Entry):
    __tablename__ = "class"

    role = db.Column(db.Unicode(200))
    abilities = db.Column(db.Unicode(200))
    powersource = db.Column(db.Unicode(200))

    filter_col_names = ["role", "powersource", "abilities"]

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                role=data.get("rolename"),
                abilities=data.get("keyabilities"),
                powersource=data.get("powersourcetext"),
                data=data,
                )

    @classmethod
    def get_filter_options(cls):
        options = super(Class, cls).get_filter_options()

        abilities = set()
        for abilities_string in options["abilities"]:
            abilities.update(set(a.strip() for a in abilities_string.split(",")))
        options["abilities"] = sorted(list(abilities))

        return options

    def as_dict(self):
        return dict(
                entry_type="class",
                id=self.id,
                name=self.name,
                role=self.role,
                abilities=[a.strip() for a in self.abilities.split(",")],
                powersource=self.powersource,
                )


class Power(db.Model, Entry):
    __tablename__ = "power"

    actiontype = db.Column(db.Unicode(200))
    classname = db.Column(db.Unicode(200))
    level = db.Column(db.Integer)
    usagetype = db.Column(db.Unicode(200))

    filter_col_names = ["actiontype", "classname", "usagetype", "level"]

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                actiontype=data.get("actiontype"),
                classname=data.get("classname"),
                level=int(data.get("level")) if data.get("level") != "" else None,
                usagetype=data.get("usagetype"),
                data=data,
                )

    @classmethod
    def get_filter_options(cls):
        options = super(Power, cls).get_filter_options()

        options["level"] = dict(
                minimum=0,
                maximum=max(options["level"]),
                )

        return options

    def as_dict(self):
        return dict(
                entry_type="power",
                id=self.id,
                name=self.name,
                actiontype=self.actiontype,
                classname=self.classname,
                level=self.level,
                usagetype=self.usagetype,
                )


class Monster(db.Model, Entry):
    __tablename__ = "monster"

    level = db.Column(db.Integer)
    grouprole = db.Column(db.Unicode(200))
    combatrole = db.Column(db.Unicode(200))

    filter_col_names = ["level", "grouprole", "combatrole"]

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                level=int(data.get("level")) if data.get("level") != "" else None,
                grouprole=data.get("grouprole", ""),
                combatrole=",".join(r.strip().lower().capitalize() for r in data.get("combatrole", "").split(",")),
                data=data,
                )

    def as_dict(self):
        return dict(
                entry_type="monster",
                id=self.id,
                name=self.name,
                level=self.level,
                grouprole=self.grouprole,
                combatrole=self.combatrole.split(","),
                )


class Item(db.Model, Entry):
    __tablename__ = "item"

    cost = db.Column(db.Integer)
    level = db.Column(db.Integer)
    rarity = db.Column(db.Unicode(200))
    category = db.Column(db.Unicode(200))

    filter_col_names = ["cost", "level"]

    @hybrid_property
    def magical(self):
        return self.rarity != ""

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                cost=int(data["costsort"]),
                level=int(data["levelsort"]),
                rarity=data.get("rarity"),
                category=data.get("category"),
                data=data,
                )

    @classmethod
    def get_filter_options(cls):
        options = super(Item, cls).get_filter_options()

        options["cost"] = dict(
                minimum=0,
                maximum=max(options["cost"]),
                )
        options["level"] = dict(
                minimum=0,
                maximum=max(options["level"]),
                )
        category_data = db.session.query(cls.magical, cls.category, func.count(cls.category)).group_by(cls.magical, cls.category).all()
        options["category"] = [(("Magical" if m else "Mundane", cat), count) for m, cat, count in category_data]

        return options

    def as_dict(self):
        return dict(
                entry_type="item",
                id=self.id,
                name=self.name,
                cost=self.cost,
                level=self.level,
                rarity=self.rarity,
                category=self.category,
                )


class Glossary(db.Model, Entry):
    __tablename__ = "glossary"

    category = db.Column(db.Unicode(200))
    glossarytype = db.Column(db.Unicode(200))

    filter_col_names = ["category", "glossarytype"]

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                category=data["category"],
                glossarytype=data["type"],
                data=data,
                )

    def as_dict(self):
        return dict(
                entry_type="monster",
                id=self.id,
                name=self.name,
                category=self.category,
                glossarytype=self.glossarytype,
                )


class Race(db.Model, Entry):
    __tablename__ = "race"

    filter_col_names = []

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                data=data,
                )

    def as_dict(self):
        return dict(
                entry_type="race",
                id=self.id,
                name=self.name,
                )


class Ritual(db.Model, Entry):
    __tablename__ = "ritual"

    level = db.Column(db.Integer)
    cost = db.Column(db.Integer)
    keyskill = db.Column(db.Unicode(200))

    filter_col_names = ["level", "cost", "keyskill"]

    @classmethod
    def from_parsed_data(cls, data):
        data, text = cls._split_text(data)
        return cls(
                id=int(data["id"]),
                name=data["name"],
                text=text,
                level=int(data["level"]),
                cost=int(data["price"]),
                keyskill=data.get("keyskilldescription"),
                data=data,
                )

    @classmethod
    def get_filter_options(cls):
        options = super(Ritual, cls).get_filter_options()

        options["cost"] = dict(
                minimum=0,
                maximum=max(options["cost"]),
                )
        options["level"] = dict(
                minimum=0,
                maximum=max(options["level"]),
                )

        return options

    def as_dict(self):
        return dict(
                entry_type="ritual",
                id=self.id,
                name=self.name,
                level=self.level,
                cost=self.cost,
                keyskill=self.keyskill,
                )


entry_types = {
        "deity": Deity,
        "feat": Feat,
        "class": Class,
        "power": Power,
        "monster": Monster,
        "item": Item,
        "glossary": Glossary,
        "race": Race,
        "ritual": Ritual,
        }
