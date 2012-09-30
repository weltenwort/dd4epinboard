# -*- encoding:utf-8 -*-
from flask import (
        Blueprint,
        #current_app,
        jsonify,
        #render_template,
        #request,
        )
#from flask.views import MethodView
#from flask.ext.login import (
        #current_user,
        #login_user,
        #login_required,
        #)

from server.db import db
from server.utils import jsonify_error
import server.models as models

filter = Blueprint("filter", __name__)


def get_entry_model(entry_type):
    return models.entry_types.get(entry_type, None)


@filter.route("/")
def get_all_filters():
    filters = dict()
    for entry_type in models.entry_types:
        filters[entry_type] = get_entry_model(entry_type).get_filter_options()
    return jsonify(options=filters)


@filter.route("/<entry_type>")
def get_entry_type_filters(entry_type):
    model = get_entry_model(entry_type)
    if model is not None:
        return jsonify(options=model.get_filter_options())
    else:
        return jsonify_error(
                reason="Unkown entry type: {}".format(entry_type),
                )
