"""Route handlers for capturing and inspecting webhook requests."""

from flask import Blueprint, request, jsonify
from hookdrop.storage import store, WebhookRequest

capture_bp = Blueprint("capture", __name__)


@capture_bp.route("/hooks/<path:hook_path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def capture_webhook(hook_path: str):
    """Catch-all endpoint that captures any incoming webhook."""
    req = WebhookRequest(
        method=request.method,
        path=f"/{hook_path}",
        headers=dict(request.headers),
        body=request.get_data(),
        query_string=request.query_string.decode("utf-8"),
    )
    store.add(req)
    return jsonify({"status": "captured", "id": req.id}), 200


@capture_bp.route("/api/requests", methods=["GET"])
def list_requests():
    """Return all captured requests, newest first."""
    return jsonify([r.to_dict() for r in store.get_all()])


@capture_bp.route("/api/requests/<request_id>", methods=["GET"])
def get_request(request_id: str):
    """Return a single captured request by ID."""
    req = store.get_by_id(request_id)
    if req is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(req.to_dict())


@capture_bp.route("/api/requests", methods=["DELETE"])
def clear_requests():
    """Clear all captured requests."""
    count = store.clear()
    return jsonify({"deleted": count})
