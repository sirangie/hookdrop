from flask import Blueprint, request, jsonify
from hookdrop.storage import RequestStore

tag_bp = Blueprint("tag", __name__)
_store: RequestStore = None


def init_tag(app, store: RequestStore):
    global _store
    _store = store
    app.register_blueprint(tag_bp)


@tag_bp.route("/requests/<request_id>/tags", methods=["POST"])
def add_tags(request_id):
    req = _store.get(request_id)
    if req is None:
        return jsonify({"error": "Not found"}), 404

    body = request.get_json(silent=True) or {}
    tags = body.get("tags", [])
    if not isinstance(tags, list):
        return jsonify({"error": "'tags' must be a list"}), 400

    tags = [str(t).strip() for t in tags if str(t).strip()]
    existing = set(req.tags if hasattr(req, "tags") else [])
    existing.update(tags)
    req.tags = sorted(existing)
    return jsonify({"id": request_id, "tags": req.tags}), 200


@tag_bp.route("/requests/<request_id>/tags", methods=["GET"])
def get_tags(request_id):
    req = _store.get(request_id)
    if req is None:
        return jsonify({"error": "Not found"}), 404
    tags = req.tags if hasattr(req, "tags") else []
    return jsonify({"id": request_id, "tags": tags}), 200


@tag_bp.route("/requests/<request_id>/tags", methods=["DELETE"])
def remove_tags(request_id):
    req = _store.get(request_id)
    if req is None:
        return jsonify({"error": "Not found"}), 404

    body = request.get_json(silent=True) or {}
    tags_to_remove = set(body.get("tags", []))
    existing = set(req.tags if hasattr(req, "tags") else [])
    req.tags = sorted(existing - tags_to_remove)
    return jsonify({"id": request_id, "tags": req.tags}), 200


@tag_bp.route("/tags", methods=["GET"])
def list_all_tags():
    all_tags: set = set()
    for req in _store.all():
        if hasattr(req, "tags"):
            all_tags.update(req.tags)
    return jsonify({"tags": sorted(all_tags)}), 200
