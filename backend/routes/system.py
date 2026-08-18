"""System endpoints: health check and rate-limit status."""

from __future__ import annotations

from flask import Blueprint

from app.cache import get_rate_limiter
from app.response import success_response
from config.logging_config import get_logger
from routes.common import get_client_ip

system_bp = Blueprint("system", __name__)
logger = get_logger("system", "INFO")
rate_limiter = get_rate_limiter()


@system_bp.route("/api/rate-limit-status")
def rate_limit_status():
    client_ip = get_client_ip()
    return success_response(
        {
            "copy": {
                "limit": rate_limiter.get_limit("copy"),
                "remaining": rate_limiter.get_remaining("copy", client_ip),
            },
            "export": {
                "limit": rate_limiter.get_limit("export"),
                "remaining": rate_limiter.get_remaining("export", client_ip),
            },
        }
    )


@system_bp.route("/health")
def health():
    """Lightweight liveness probe — does not touch the DB."""

    return success_response({"status": "ok"})