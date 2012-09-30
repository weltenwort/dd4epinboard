# -*- encoding:utf-8 -*-
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.zen import Test, ZenTest

from server import create_app
from server.db import (
        CreateDbCommand,
        CreateUserCommand,
        CreateUserDbCommand,
        ImportDataCommand,
        )

manager = Manager(create_app())
manager.add_command("assets", ManageAssets())
manager.add_command("test", Test())
manager.add_command("zen", ZenTest())
manager.add_command("create_user_db", CreateUserDbCommand())
manager.add_command("create_data_db", CreateDbCommand(None))
manager.add_command("create_user", CreateUserCommand())
manager.add_command("import_data", ImportDataCommand())


if __name__ == "__main__":
    manager.run()
