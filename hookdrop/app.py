from flask import Flask
from hookdrop.storage import RequestStore
from hookdrop.routes.capture import capture_webhook, list_requests, get_request, clear_requests
from hookdrop.routes.replay import init_replay
from hookdrop.routes.inspect import init_inspect
from hookdrop.routes.export import init_export
from hookdrop.routes.filter import init_filter
from hookdrop.routes.stats import init_stats
from hookdrop.routes.search import init_search
from hookdrop.routes.tag import init_tag


def create_app(store: RequestStore = None) -> Flask:
    app = Flask(__name__)
    if store is None:
        store = RequestStore()

    app.add_url_rule("/hooks/<path:hook_path>", view_func=lambda **kw: capture_webhook(store, **kw), methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    app.add_url_rule("/requests", view_func=lambda: list_requests(store), methods=["GET"])
    app.add_url_rule("/requests/<request_id>", view_func=lambda request_id: get_request(store, request_id), methods=["GET"])
    app.add_url_rule("/requests", view_func=lambda: clear_requests(store), methods=["DELETE"])

    init_replay(app, store)
    init_inspect(app, store)
    init_export(app, store)
    init_filter(app, store)
    init_stats(app, store)
    init_search(app, store)
    init_tag(app, store)

    return app
