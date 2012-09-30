# -*- encoding:utf-8 -*-
import json
import math

from flask import (
        Blueprint,
        current_app,
        jsonify,
        #render_template,
        request,
        )
#from flask.views import MethodView
#from flask.ext.login import (
        #current_user,
        #login_user,
        #login_required,
        #)

from server.db import db
from server.utils import jsonify_error
from server.utils.search import create_query
import server.models as models

entry = Blueprint("entry", __name__)


def get_entry_model(entry_type):
    return models.entry_types.get(entry_type, None)


@entry.route("/<entry_type>", methods=["GET", "POST"])
def filter_entries(entry_type):
    objects_per_page = current_app.config.get("OBJECTS_PER_PAGE", 10)

    query_dict = json.loads(request.json.get("query", "{}"))
    query_dict.setdefault("order_by", []).append(dict(
        field="name",
        direction="asc",
        ))

    page = int(request.json.get("page", 1))

    model = get_entry_model(entry_type)
    if model is not None:
        query = create_query(db.session, model, query_dict)
        object_count = query.count()
        limited_query = query.offset((page - 1) * objects_per_page)\
                .limit(objects_per_page)
        return jsonify(
                page=page,
                total_pages=int(math.ceil(\
                        float(object_count) / float(objects_per_page))),
                total_object_count=object_count,
                objects=[entry.data for entry in limited_query.all()],
                )
    else:
        return jsonify_error(
                reason="Unkown entry type: {}".format(entry_type),
                )


@entry.route("/<entry_type>/<entry_id>")
def get_entry(entry_type, entry_id):
    if entry_type in models.entry_types:
        model = models.entry_types[entry_type]
        entry = model.query.filter_by(id=entry_id).first()
        return entry.text
