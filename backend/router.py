"""Application factory and blueprint registration."""

from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from config.logging_config import get_logger
from routes.favorites import favorites_bp
from routes.projects import projects_bp
from routes.reports import reports_bp
from routes.stats import stats_bp
from routes.system import system_bp
from routes.trends import trends_bp

logger = get_logger("router", "INFO")

app = Flask(__name__, static_folder="../images", static_url_path="/images")
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        }
    },
)

app.register_blueprint(projects_bp, url_prefix="/api")
app.register_blueprint(stats_bp, url_prefix="/api")
app.register_blueprint(reports_bp, url_prefix="/api")
app.register_blueprint(trends_bp, url_prefix="/api")
app.register_blueprint(favorites_bp, url_prefix="/api")
# system_bp carries its own prefix on each route: /api/rate-limit-status and /health.
app.register_blueprint(system_bp)