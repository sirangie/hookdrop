import json
import csv
import io
from flask import Blueprint, current_app, jsonify, Response, request

export_bp = Blueprint("export", __name__)


def init_export(app):
    app.register_blueprint(export_bp)


@export_bp.route("/requests/export", methods=["GET"])
def export_requests():
    """Export all captured requests as JSON or CSV."""
    fmt = request.args.get("format", "json").lower()
    store = current_app.config["REQUEST_STORE"]
    requests_list = [r.to_dict() for r in store.all()]

    if fmt == "csv":
        return _export_csv(requests_list)
    elif fmt == "json":
        return _export_json(requests_list)
    else:
        return jsonify({"error": f"Unsupported format: {fmt}. Use 'json' or 'csv'."}), 400


def _export_json(requests_list):
    output = json.dumps(requests_list, indent=2)
    return Response(
        output,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=hookdrop_requests.json"},
    )


def _export_csv(requests_list):
    if not requests_list:
        fieldnames = ["id", "method", "path", "timestamp", "body"]
    else:
        fieldnames = ["id", "method", "path", "timestamp", "body"]

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in requests_list:
        flat = {
            "id": row.get("id", ""),
            "method": row.get("method", ""),
            "path": row.get("path", ""),
            "timestamp": row.get("timestamp", ""),
            "body": row.get("body", ""),
        }
        writer.writerow(flat)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=hookdrop_requests.csv"},
    )
