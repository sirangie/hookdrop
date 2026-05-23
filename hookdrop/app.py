from flask import Flask
from hookdrop.storage import RequestStore
from hookdrop.routes.capture import capture_webhook, list_requests, get_request, clear_requests
from hookdrop.routes.replay import init_replay
from hookdrop.routes.inspect import init_inspect
from hookdrop.routes.export import init_export
from hookdrop.routes.filter import init_filter
from hookdrop.routes.stats import init_stats
from hookdrop.routes.search import init_search


def create_app(max_requests: int = 200) -> Flask:
    app = Flask(__name__)
    store = RequestStore(max_requests=max_requests)

    app.config["store"] = store

    app.add_url_rule("/hook/<path:subpath>", view_func=lambda **kw: capture_webhook(store, **kw), methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    app.add_url_rule("/requests", view_func=lambda: list_requests(store), methods=["GET"])
    app.add_url_rule("/requests/<req_id>", view_func=lambda req_id: get_request(store, req_id), methods=["GET"])
    app.add_url_rule("/requests", view_func=lambda: clear_requests(store), methods=["DELETE"])

    init_replay(app, store)
    init_inspect(app, store)
    init_export(app, store)
    init_filter(app, store)
    init_stats(app, store)
    init_search(app, store)

    return app
