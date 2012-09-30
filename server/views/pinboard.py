# -*- encoding:utf-8 -*-
from flask import (
        Blueprint,
        jsonify,
        #render_template,
        request,
        )
from flask.views import MethodView
from flask.ext.login import (
        current_user,
        login_required,
        )

from server.db import db
from server.utils import jsonify_error
import server.models as models

pinboard = Blueprint("pinboard", __name__)


class PinboardAPI(MethodView):
    decorators = [login_required, ]

    def get(self, pinboard_id):
        if pinboard_id is None:
            # list pinboards
            owned_pinboards = list(current_user.owned_pinboards)
            other_pinboards = models.Pinboard.query.filter(models.Pinboard.owner != current_user, models.Pinboard.public == True).all()

            return jsonify(
                    pinboards={p.id: p.as_dict() for p in owned_pinboards + other_pinboards},
                    )
        else:
            p = models.Pinboard.query.get(pinboard_id)
            if p is not None and (p.public or p.owner_username == current_user.username):
                return jsonify(pinboard=p.as_dict(full=True))
            else:
                return jsonify_error(
                        reason="invalid_pinboard_id",
                        )

    def post(self):
        name = request.json.get("name")
        description = request.json.get("description")
        public = request.json.get("public", False)

        #TODO: handle exceptions
        p = models.Pinboard(
                name=name,
                description=description,
                public=public,
                owner=current_user,
                )

        db.session.add(p)
        db.session.commit()

        return jsonify(
                status="ok",
                pinboard=p.as_dict(),
                )

    def put(self, pinboard_id):
        operation = request.json.get("operation")
        p = models.Pinboard.query.get(pinboard_id)

        if p is not None and p.owner == current_user or current_user.admin:
            if operation == "update":
                p_data = request.json.get("pinboard")
                name = p_data.get("name")
                description = p_data.get("description")
                public = p_data.get("public", False)

                p.name = name
                p.description = description
                p.public = public

                db.session.commit()

                return jsonify(
                        status="ok",
                        pinboard=p.as_dict(full=True),
                        )
            elif operation == "add_entry":
                entry_data = request.json["entry"]
                entry_type = entry_data["entry_type"]
                entry_id = entry_data["id"]

                try:
                    p.add_entry(entry_type, entry_id)
                    db.session.commit()
                    return jsonify(
                            status="ok",
                            pinboard=p.as_dict(full=True),
                            )
                except models.Pinboard.EntryAlreadyPresentError:
                    return jsonify_error(
                            reason="entry_already_in_pinboard",
                            )
            elif operation == "remove_entry":
                entry_data = request.json["entry"]
                entry_type = entry_data["entry_type"]
                entry_id = entry_data["id"]

                try:
                    p.remove_entry(entry_type, entry_id)
                    db.session.commit()
                    return jsonify(
                            status="ok",
                            pinboard=p.as_dict(full=True),
                            )
                except models.Pinboard.EntryNotPresentError:
                    return jsonify_error(
                            reason="entry_not_present_in_pinboard",
                            )
            else:
                return jsonify_error(
                        reason="invalid_operation",
                        )
        else:
            return jsonify_error(
                    reason="invalid_pinboard_id",
                    )

    def delete(self, pinboard_id):
        p = models.Pinboard.query.get(pinboard_id)

        if p is not None and p.owner == current_user or current_user.admin:
            db.session.delete(p)
            db.session.commit()
            return jsonify(
                    status="ok",
                    )
        else:
            return jsonify_error(
                    reason="invalid_pinboard_id",
                    )


pinboard_api_view = PinboardAPI.as_view("pinboard_api")
pinboard.add_url_rule("/", view_func=pinboard_api_view, methods=["GET", ], defaults={"pinboard_id": None})
pinboard.add_url_rule("/", view_func=pinboard_api_view, methods=["POST", ], )
pinboard.add_url_rule("/<int:pinboard_id>", view_func=pinboard_api_view, methods=["GET", "PUT", "DELETE"], )
