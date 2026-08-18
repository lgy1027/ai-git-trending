"""Trend analysis endpoints backed by `app.analyzer.analyze_trends`."""

from __future__ import annotations

from flask import Blueprint, request

from app.analyzer import analyze_trends
from app.response import ErrorCode, error_response, success_response
from config.logging_config import get_logger

trends_bp = Blueprint("trends", __name__)
logger = get_logger("trends", "INFO")

_ALLOWED_DAYS = {1, 7, 30, 182, 365}


def _parse_days() -> int:
    days = request.args.get("days", 7, type=int) or 7
    return days if days in _ALLOWED_DAYS else 7


@trends_bp.route("/trends")
def get_trends():
    try:
        return success_response(analyze_trends(_parse_days()))
    except Exception as exc:
        logger.error("Failed to analyze trends: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve trends", 500)


@trends_bp.route("/trend-data")
def get_trend_data():
    try:
        trends = analyze_trends(_parse_days())
        items = [
            {
                "label": "热门项目",
                "value": len(trends.get("topProjects", [])),
                "change": 0,
                "colorClass": "text-cyan-300",
            },
            {
                "label": "飙升项目",
                "value": len(trends.get("surgingProjects", [])),
                "change": 0,
                "colorClass": "text-emerald-300",
            },
            {
                "label": "技术领域",
                "value": len(trends.get("techDomains", [])),
                "change": 0,
                "colorClass": "text-fuchsia-300",
            },
        ]
        return success_response(items)
    except Exception as exc:
        logger.error("Failed to build trend data: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve trend data", 500)