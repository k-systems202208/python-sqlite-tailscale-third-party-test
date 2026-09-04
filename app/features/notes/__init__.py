"""Notes feature for the third-party sample application."""


def register(app) -> None:
    from .routes import bp

    app.register_blueprint(bp)
