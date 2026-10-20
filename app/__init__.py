"""AMWA ALP Attendance Service.

A small piece of the AMWA Adult Literacy/ESL Program (ALP) management
platform: tracks class sessions and student check-ins, and flags students
whose attendance drops below the program's follow-up threshold so the
program manager can reach out before they disengage.
"""

from flask import Flask

from .routes import bp
from .store import Store


def create_app(store: Store | None = None) -> Flask:
    app = Flask(__name__)
    app.config["STORE"] = store or Store()
    app.register_blueprint(bp)
    return app
