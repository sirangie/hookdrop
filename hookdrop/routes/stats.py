from flask import Blueprint, jsonify
from collections import Counter
from hookdrop.storage import RequestStore

stats_bp = Blueprint("stats", __name__)
_store: RequestStore = None


def init_stats(store: RequestStore):
    global _store
    _store = store
    return stats_bp


@stats_bp.route("/stats", methods=["GET"])
def request_stats():
    requests = _store.all()

    if not requests:
        return jsonify({
            "total": 0,
            "by_method": {},
            "by_status": {},
            "by_content_type": {},
            "most_recent": None,
        })

    methods = Counter(r.method for r in requests)
    statuses = Counter(r.status_code for r in requests)
    content_types = Counter(
        r.headers.get("Content-Type", "unknown").split(";")[0].strip()
        for r in requests
    )

    most_recent = max(requests, key=lambda r: r.timestamp)

    return jsonify({
        "total": len(requests),
        "by_method": dict(methods),
        "by_status": {str(k): v for k, v in statuses.items()},
        "by_content_type": dict(content_types),
        "most_recent": most_recent.id,
    })
