"""Report listing / content / download / copy endpoints."""

from __future__ import annotations

import os

from flask import Blueprint, send_from_directory

from app.cache import get_rate_limiter
from app.response import ErrorCode, error_response, success_response
from config.logging_config import get_logger
from config.settings import HTML_DIR, MD_DIR
from routes.common import (
    count_projects_in_report,
    get_client_ip,
    get_report_data_from_filename,
    validate_date_string,
    validate_format_string,
)

reports_bp = Blueprint("reports", __name__)
logger = get_logger("reports", "INFO")
rate_limiter = get_rate_limiter()


@reports_bp.route("/reports")
def list_reports():
    try:
        files = os.listdir(MD_DIR)
        md_files = sorted((f for f in files if f.endswith(".md")), reverse=True)

        reports = []
        for filename in md_files:
            report_data = get_report_data_from_filename(filename)
            if not report_data:
                continue
            with open(report_data["path"], "r", encoding="utf-8") as handle:
                content = handle.read()
            reports.append(
                {
                    "date": report_data["date"],
                    "project_count": count_projects_in_report(content),
                }
            )

        return success_response(reports)
    except Exception as exc:
        logger.error("Failed to load reports: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve reports", 500)


@reports_bp.route("/report/<date_str>")
def get_report_content(date_str: str):
    is_valid, error_message = validate_date_string(date_str)
    if not is_valid:
        return error_response(ErrorCode.VALIDATION_ERROR, error_message, 400)

    filename = f"github_trending_{date_str}.md"
    filepath = os.path.join(MD_DIR, filename)
    if not os.path.exists(filepath):
        return error_response(ErrorCode.NOT_FOUND, "Report not found", 404)

    try:
        with open(filepath, "r", encoding="utf-8") as handle:
            content = handle.read()
        return success_response(
            {
                "date": date_str,
                "content": content,
                "project_count": count_projects_in_report(content),
            }
        )
    except Exception as exc:
        logger.error("Failed to load report %s: %s", date_str, exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve report", 500)


@reports_bp.route("/download/<date_str>/<format>")
def download_report(date_str: str, format: str):
    is_valid, error_message = validate_date_string(date_str)
    if not is_valid:
        return error_response(ErrorCode.VALIDATION_ERROR, error_message, 400)
    if not validate_format_string(format):
        return error_response(ErrorCode.INVALID_FORMAT, "Invalid format, expected html or md", 400)

    client_ip = get_client_ip()
    allowed, _ = rate_limiter.check_limit("export", client_ip)
    if not allowed:
        return error_response(
            ErrorCode.TOO_MANY_REQUESTS,
            "Daily export limit reached",
            429,
            data={
                "limit": rate_limiter.get_limit("export"),
                "remaining": 0,
            },
        )

    target_dir = HTML_DIR if format == "html" else MD_DIR
    filename = f"github_trending_{date_str}.{format}"
    if not os.path.exists(os.path.join(target_dir, filename)):
        return error_response(ErrorCode.NOT_FOUND, "File not found", 404)

    rate_limiter.increment("export", client_ip)
    remaining = rate_limiter.get_remaining("export", client_ip)

    response = send_from_directory(target_dir, filename, as_attachment=True)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.get_limit("export"))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response


@reports_bp.route("/copy/<date_str>")
def copy_report(date_str: str):
    is_valid, error_message = validate_date_string(date_str)
    if not is_valid:
        return error_response(ErrorCode.VALIDATION_ERROR, error_message, 400)

    client_ip = get_client_ip()
    allowed, _ = rate_limiter.check_limit("copy", client_ip)
    if not allowed:
        return error_response(
            ErrorCode.TOO_MANY_REQUESTS,
            "Daily copy limit reached",
            429,
            data={
                "limit": rate_limiter.get_limit("copy"),
                "remaining": 0,
            },
        )

    filename = f"github_trending_{date_str}.md"
    filepath = os.path.join(MD_DIR, filename)
    if not os.path.exists(filepath):
        return error_response(ErrorCode.NOT_FOUND, "Report not found", 404)

    with open(filepath, "r", encoding="utf-8") as handle:
        content = handle.read()

    rate_limiter.increment("copy", client_ip)
    remaining = rate_limiter.get_remaining("copy", client_ip)
    return success_response(
        {
            "content": content,
            "rate_limit": {
                "limit": rate_limiter.get_limit("copy"),
                "remaining": remaining,
            },
        }
    )