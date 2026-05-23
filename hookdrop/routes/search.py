from flask import Blueprint, request, jsonify
from hookdrop.storage import RequestStore

search_bp = Blueprint("search", __name__)
_store: RequestStore = None


def init_search(app, store: RequestStore):
    global _store
    _store = store
    app.register_blueprint(search_bp)


@search_bp.route("/search", methods=["GET"])
def search_requests():
    """Search captured requests by header value or body substring."""
    header_key = request.args.get("header_key", "").strip()
    header_value = request.args.get("header_value", "").strip()
    body_contains = request.args.get("body_contains", "").strip()
    path_contains = request.args.get("path_contains", "").strip()

    if not any([header_key, header_value, body_contains, path_contains]):
        return jsonify({"error": "At least one search parameter is required"}), 400

    results = []
    for req in _store.all():
        if path_contains and path_contains.lower() not in req.path.lower():
            continue

        if header_key:
            matched_header = next(
                (v for k, v in req.headers.items() if k.lower() == header_key.lower()),
                None,
            )
            if matched_header is None:
                continue
            if header_value and header_value.lower() not in matched_header.lower():
                continue

        if body_contains:
            body_str = req.body if isinstance(req.body, str) else ""
            if body_contains.lower() not in body_str.lower():
                continue

        results.append(req.to_dict())

    return jsonify({"count": len(results), "results": results}), 200
