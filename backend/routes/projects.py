"""Project-related API routes."""

from __future__ import annotations

import urllib.parse

from flask import Blueprint, request

from app.database import ProjectDatabase
from app.response import ErrorCode, error_response, get_pagination_params, paginate_response, success_response
from config.logging_config import get_logger
from routes.common import find_project_details, validate_date_string, validate_project_name

projects_bp = Blueprint("projects", __name__)
logger = get_logger("projects", "INFO")
db = ProjectDatabase()


def decode_uri_component(value: str) -> str:
    try:
        return urllib.parse.unquote(value)
    except Exception:
        return value


@projects_bp.route("/project/<project_name>")
def get_project_details(project_name: str):
    decoded_project_name = decode_uri_component(project_name)
    is_valid, error_message = validate_project_name(decoded_project_name)
    if not is_valid:
        return error_response(ErrorCode.VALIDATION_ERROR, error_message, 400)

    try:
        project = find_project_details(decoded_project_name)
        if not project:
            return error_response(ErrorCode.NOT_FOUND, "Project not found", 404)
        return success_response(project)
    except Exception as exc:
        logger.error("Failed to load project %s: %s", decoded_project_name, exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve project details", 500)


@projects_bp.route("/project", methods=["GET", "POST"])
def get_project_details_api():
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        project_name = payload.get("name") or payload.get("project_name")
    else:
        project_name = request.args.get("name") or request.args.get("project_name")

    if not project_name:
        return error_response(ErrorCode.VALIDATION_ERROR, "Project name is required", 400)

    return get_project_details(project_name)


@projects_bp.route("/projects/<date_str>")
def get_projects_by_date(date_str: str):
    is_valid, error_message = validate_date_string(date_str)
    if not is_valid:
        return error_response(ErrorCode.VALIDATION_ERROR, error_message, 400)

    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM summarized_projects WHERE summary_date = ? ORDER BY stars DESC",
                (date_str,),
            )
            rows = cursor.fetchall()
            if not rows:
                return success_response([])

            columns = [description[0] for description in cursor.description]
            projects = [dict(zip(columns, row)) for row in rows]
            return success_response(projects)
    except Exception as exc:
        logger.error("Failed to load projects for %s: %s", date_str, exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve projects", 500)


@projects_bp.route("/projects")
def get_projects():
    page, page_size = get_pagination_params(request)
    sort_by = request.args.get("sort_by", "stars")
    order = request.args.get("order", "desc")
    language_filter = request.args.get("language")
    tech_domain_filter = request.args.get("tech_domain")
    min_stars = request.args.get("min_stars", type=int)
    max_stars = request.args.get("max_stars", type=int)
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    search = request.args.get("search")

    safe_sort_fields = {
        "stars": "stars",
        "forks": "forks",
        "contributor_count": "contributor_count",
        "name": "name",
        "summary_date": "summary_date",
    }
    safe_sort = safe_sort_fields.get(sort_by, "stars")
    safe_order = "DESC" if order == "desc" else "ASC"

    filters = ["1=1"]
    params: list[object] = []

    if language_filter:
        filters.append("language = ?")
        params.append(language_filter)
    if tech_domain_filter:
        filters.append("tech_domain = ?")
        params.append(tech_domain_filter)
    if min_stars is not None:
        filters.append("stars >= ?")
        params.append(min_stars)
    if max_stars is not None:
        filters.append("stars <= ?")
        params.append(max_stars)
    if date_from:
        filters.append("summary_date >= ?")
        params.append(date_from)
    if date_to:
        filters.append("summary_date <= ?")
        params.append(date_to)
    if search:
        filters.append("(name LIKE ? OR description LIKE ?)")
        keyword = f"%{search}%"
        params.extend([keyword, keyword])

    where_clause = " AND ".join(filters)

    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM summarized_projects WHERE {where_clause}", params)
            total = cursor.fetchone()[0] or 0

            offset = (page - 1) * page_size
            query = (
                f"SELECT * FROM summarized_projects WHERE {where_clause} "
                f"ORDER BY {safe_sort} {safe_order} LIMIT ? OFFSET ?"
            )
            cursor.execute(query, params + [page_size, offset])
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            items = [dict(zip(columns, row)) for row in rows]

        return success_response(paginate_response(items, total, page, page_size))
    except Exception as exc:
        logger.error("Failed to load project list: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve projects", 500)
