from flask import jsonify


def jsonify_error(reason, code=500):
    return jsonify(
            status="error",
            status_code=code,
            reason=reason,
            ), code
