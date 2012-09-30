from flask import jsonify
from flask.ext.login import LoginManager

from models.users import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def handle_unauthorized():
    return jsonify(error="unauthorized")
