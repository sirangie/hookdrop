from flask import Blueprint, jsonify, request
from hookdrop.storage import RequestStore

filter_bp = Blueprint("filter", __name__)
_store: RequestStore = None


def init_filter(store: RequestStore):
    global _store
    _store = store
    return filter_bp


@filter_bp.route("/requests/filter", methods=["GET"])
def filter_requests():
    """Filter captured requests by method, path, or header key/value."""
    method = request.args.get("method", "").upper()
    path_contains = request.args.get("path", "")
    header_key = request.args.get("header_key", "")
    header_value = request.args.get("header_value", "")
    status_code = request.args.get("status_code", type=int)

    results = _store.all()

    if method:
        results = [r for r in results if r.method.upper() == method]

    if path_contains:
        results = [r for r in results if path_contains in r.path]

    if header_key:
        hk_lower = header_key.lower()
        if header_value:
            results = [
                r for r in results
                if r.headers.get(hk_lower, "").lower() == header_value.lower()
                or r.headers.get(header_key, "").lower() == header_value.lower()
            ]
        else:
            results = [
                r for r in results
                if hk_lower in {k.lower() for k in r.headers}
            ]

    if status_code is not None:
        results = [r for r in results if r.status_code == status_code]

    return jsonify({
        "count": len(results),
        "requests": [r.to_dict() for r in results],
    })
