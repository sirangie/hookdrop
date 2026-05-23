from flask import Blueprint, jsonify, current_app

inspect_bp = Blueprint("inspect", __name__)


def init_inspect(app):
    app.register_blueprint(inspect_bp)


@inspect_bp.route("/inspect/<request_id>", methods=["GET"])
def inspect_request(request_id):
    """Return detailed breakdown of a captured webhook request."""
    store = current_app.config["REQUEST_STORE"]
    req = store.get(request_id)

    if req is None:
        return jsonify({"error": "Request not found"}), 404

    data = req.to_dict()

    # Build a structured inspection payload
    inspection = {
        "id": data["id"],
        "summary": {
            "method": data["method"],
            "path": data["path"],
            "timestamp": data["timestamp"],
            "content_type": data["headers"].get("Content-Type", "unknown"),
            "body_size_bytes": len((data.get("body") or "").encode("utf-8")),
        },
        "headers": data["headers"],
        "query_params": data["query_params"],
        "body": data.get("body"),
        "parsed_body": _try_parse_body(data.get("body"), data["headers"]),
    }

    return jsonify(inspection), 200


@inspect_bp.route("/inspect/<request_id>/headers", methods=["GET"])
def inspect_headers(request_id):
    """Return only the headers of a captured request."""
    store = current_app.config["REQUEST_STORE"]
    req = store.get(request_id)

    if req is None:
        return jsonify({"error": "Request not found"}), 404

    return jsonify({"id": request_id, "headers": req.to_dict()["headers"]}), 200


def _try_parse_body(body, headers):
    """Attempt to parse body as JSON if content type suggests it."""
    if not body:
        return None
    content_type = headers.get("Content-Type", "")
    if "application/json" in content_type:
        import json
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            return None
    return None
