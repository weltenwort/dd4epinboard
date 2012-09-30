# -*- encoding:utf-8 -*-
from flask import (
        Blueprint,
        jsonify,
        render_template,
        request,
        )
from flask.views import MethodView
from flask.ext.login import (
        current_user,
        login_user,
        logout_user,
        #login_required,
        )

from server.db import db
from server.utils import jsonify_error
import server.models as models

frontend = Blueprint("frontend", __name__)


@frontend.route("/")
def index():
    return render_template("index.jade")


class SessionAPI(MethodView):
    def get(self):
        return jsonify(username=current_user.get_id())

    def post(self):
        username = request.json["username"]
        password = request.json["password"]

        user = models.User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return jsonify(status="ok", username=current_user.get_id())
        else:
            return jsonify_error(
                    reason="invalid_username_or_password",
                    )

    def put(self):
        username = request.json["username"]
        password = request.json["password"]

        if current_user.is_anonymous():
            try:
                pass
            except:
                pass
        elif current_user.is_authenticated()\
                and username == current_user.username:
            current_user.password = password
            db.session.commit()
            return jsonify(status="ok")
        else:
            return jsonify_error(
                    reason="invalid_session",
                    )

    def delete(self):
        if current_user.is_authenticated():
            logout_user()
        return self.get()


frontend.add_url_rule("/session", view_func=SessionAPI.as_view("session_api"))
