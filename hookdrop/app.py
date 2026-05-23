from flask import Flask
from hookdrop.storage import RequestStore
from hookdrop.routes.capture import capture_bp, init_capture
from hookdrop.routes.replay import replay_bp, init_replay


def create_app(max_requests: int = 200) -> Flask:
    """Application factory — wires up blueprints and shared store."""
    app = Flask(__name__)

    store = RequestStore(max_requests=max_requests)

    init_capture(store)
    init_replay(store)

    app.register_blueprint(capture_bp)
    app.register_blueprint(replay_bp)

    # Expose store on app for testing convenience
    app.store = store

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=9000, debug=True)
