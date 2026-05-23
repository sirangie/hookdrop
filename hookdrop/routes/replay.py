from flask import Blueprint, jsonify, request as flask_request
import requests
from hookdrop.storage import RequestStore

replay_bp = Blueprint("replay", __name__)
_store: RequestStore = None


def init_replay(store: RequestStore):
    global _store
    _store = store


@replay_bp.route("/replay/<request_id>", methods=["POST"])
def replay_request(request_id: str):
    """Replay a previously captured webhook request to a target URL."""
    stored = _store.get(request_id)
    if stored is None:
        return jsonify({"error": "Request not found"}), 404

    body = flask_request.get_json(silent=True) or {}
    target_url = body.get("target_url")
    if not target_url:
        return jsonify({"error": "target_url is required"}), 400

    # Filter out hop-by-hop headers
    skip_headers = {"host", "content-length", "transfer-encoding", "connection"}
    headers = {
        k: v
        for k, v in stored.headers.items()
        if k.lower() not in skip_headers
    }

    try:
        resp = requests.request(
            method=stored.method,
            url=target_url,
            headers=headers,
            data=stored.body,
            timeout=10,
        )
        return jsonify({
            "replayed": True,
            "request_id": request_id,
            "target_url": target_url,
            "status_code": resp.status_code,
            "response_body": resp.text[:500],
        }), 200
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": str(exc)}), 502
