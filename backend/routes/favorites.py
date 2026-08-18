"""Favorites API: anonymous client_id based bookmarks."""

from __future__ import annotations

import re
from flask import Blueprint, request

from app.database import ProjectDatabase
from app.response import ErrorCode, error_response, success_response
from config.logging_config import get_logger

favorites_bp = Blueprint("favorites", __name__)
logger = get_logger("favorites", "INFO")
db = ProjectDatabase()

CLIENT_ID_RE = re.compile(r"^[a-zA-Z0-9-]{8,64}$")


def _validate_client_id(value: str | None) -> tuple[bool, str | None]:
    if not value:
        return False, "client_id is required"
    if not CLIENT_ID_RE.match(value):
        return False, "Invalid client_id format"
    return True, None


@favorites_bp.route("/favorites", methods=["GET"])
def list_favorites():
    client_id = request.args.get("client_id")
    ok, msg = _validate_client_id(client_id)
    if not ok:
        return error_response(ErrorCode.VALIDATION_ERROR, msg, 400)

    try:
        names = db.list_favorites(client_id)
        if not names:
            return success_response({"items": [], "total": 0})

        placeholders = ",".join("?" for _ in names)
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT name, url, description, language, stars, forks,
                       contributor_count, created_at, updated_at,
                       open_issues, watchers, summary_date
                FROM summarized_projects
                WHERE name IN ({placeholders})
                """,
                names,
            )
            rows = cursor.fetchall()
            columns = [d[0] for d in cursor.description]
            items = [dict(zip(columns, row)) for row in rows]

        return success_response({"items": items, "total": len(items)})
    except Exception as exc:
        logger.error("Failed to list favorites for %s: %s", client_id, exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to load favorites", 500)


@favorites_bp.route("/favorites", methods=["POST"])
def add_favorite():
    payload = request.get_json(silent=True) or {}
    client_id = payload.get("client_id") or request.args.get("client_id")
    project_name = payload.get("project_name") or payload.get("name")

    ok, msg = _validate_client_id(client_id)
    if not ok:
        return error_response(ErrorCode.VALIDATION_ERROR, msg, 400)
    if not project_name:
        return error_response(ErrorCode.VALIDATION_ERROR, "project_name is required", 400)
    if not re.match(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$", project_name):
        return error_response(ErrorCode.VALIDATION_ERROR, "Invalid project_name format", 400)

    try:
        added = db.add_favorite(client_id, project_name)
        return success_response({"added": added, "project_name": project_name})
    except Exception as exc:
        logger.error("Failed to add favorite %s/%s: %s", client_id, project_name, exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to add favorite", 500)


@favorites_bp.route("/favorites", methods=["DELETE"])
def remove_favorite():
    payload = request.get_json(silent=True) or {}
    client_id = payload.get("client_id") or request.args.get("client_id")
    project_name = payload.get("project_name") or payload.get("name")

    ok, msg = _validate_client_id(client_id) if client_id else (False, "client_id is required")
    if not ok:
        return error_response(ErrorCode.VALIDATION_ERROR, msg, 400)
    if not project_name:
        return error_response(ErrorCode.VALIDATION_ERROR, "project_name is required", 400)
    if not re.match(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$", project_name):
        return error_response(ErrorCode.VALIDATION_ERROR, "Invalid project_name format", 400)

    try:
        removed = db.remove_favorite(client_id, project_name)
        return success_response({"removed": removed, "project_name": project_name})
    except Exception as exc:
        logger.error("Failed to remove favorite %s/%s: %s", client_id, project_name, exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to remove favorite", 500)