import glob
import os

from flask.ext.script import Command, Option
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

import server.models as models
import server.parser as parser


class CreateDbCommand(Command):
    """Creates an empty database."""

    def __init__(self, bind_name, *args, **kwargs):
        super(CreateDbCommand, self).__init__(*args, **kwargs)
        self.bind_name = bind_name

    def run(self):
        #db.drop_all(bind=[self.bind_name, ])
        db.create_all(bind=[self.bind_name, ])


class CreateUserDbCommand(Command):
    """Creates a user database with a default user."""

    option_list = (
            Option('--admin-username', '-u', type=unicode,\
                    dest='admin_username', default="admin"),
            Option('--admin-password', '-p', type=unicode,\
                    dest='admin_password', default="admin"),
            )

    def run(self, admin_username, admin_password):
        db.drop_all(bind=["users", ])
        db.create_all(bind=["users", ])
        admin_user = models.User(
                username=unicode(admin_username),
                password=admin_password,
                admin=True,
                )
        db.session.add(admin_user)
        db.session.commit()


class CreateUserCommand(Command):
    """Creates a user in thedatabase."""

    option_list = (
            Option('username', type=unicode),
            Option('password', type=unicode),
            )

    def run(self, username, password):
        user = models.User(
                username=unicode(username),
                password=password,
                admin=False,
                )
        db.session.add(user)
        db.session.commit()


class ImportDataCommand(Command):
    """Imports data into the database."""

    option_list = (
            Option("--data-type", "-t", type=unicode, dest="data_type",\
                    required=True),
            Option("--file-pattern", "-p", type=unicode,\
                    dest="file_pattern", required=True),
            Option("--xml-file", "-x", type=unicode,\
                    dest="xml_file", default=None),
            )

    def run(self, data_type, file_pattern, xml_file):
        try:
            import progressbar
            progress = progressbar.ProgressBar(
                    widgets=[
                        "Parsing Files ",
                        progressbar.Percentage(),
                        " ",
                        progressbar.Bar(),
                        ],
                    )
        except:
            progress = list

        catalog = parser.MergedCatalog([
            parser.XmlFileCatalog(xml_file),
            parser.BlockFileCatalog(glob.glob(file_pattern),\
                    parser.get_block_parser(data_type)(data_type)),
            ])
        if catalog.has_model(data_type):
            db.session.query(catalog.get_model(data_type)).delete()
            catalog.parse()
            for entry_id in progress(catalog.get_entry_ids()):
                entry = catalog.get_entry_model(entry_id)
                db.session.add(entry)
            print(u"Committing to database...")
            db.session.commit()
        else:
            print("Unknown data type: {}".format(data_type))

    def run_old(self, data_pattern, data_type):
        parser_cls = parser.parsers.get(data_type, None)

        try:
            import progressbar
            progress = progressbar.ProgressBar(
                    widgets=[
                        "Parsing Files ",
                        progressbar.Percentage(),
                        " ",
                        progressbar.Bar(),
                        ],
                    )
        except:
            progress = list

        if parser_cls is not None:
            data_parser = parser_cls()
            db.session.query(data_parser.model).delete()
            for page_filename in progress(glob.glob(data_pattern)):
                #entry_id = unicode("{}_{}".format(data_type,\
                        #os.path.splitext(os.path.basename(page_filename))[0]))
                entry_id = int(os.path.splitext(os.path.basename(page_filename\
                        ))[0])
                with open(page_filename, "r") as fp:
                    entry = data_parser.parse_to_model(entry_id,\
                            fp.read().decode("utf-8"))
                    db.session.add(entry)
            print(u"Committing to database...")
            db.session.commit()

        else:
            print("Unknown data type: {}".format(data_type))
