"""Project-related API routes."""

from __future__ import annotations

import os
import re
import urllib.parse

from flask import Blueprint, request

from app.database import ProjectDatabase
from app.response import ErrorCode, error_response, get_pagination_params, paginate_response, success_response
from config.logging_config import get_logger
from config.settings import MD_DIR
from routes.common import find_project_details, validate_date_string, validate_project_name

projects_bp = Blueprint("projects", __name__)
logger = get_logger("projects", "INFO")
db = ProjectDatabase()


def decode_uri_component(value: str) -> str:
    try:
        return urllib.parse.unquote(value)
    except Exception:
        return value


# 报告主标题行：`# owner/repo - 深度分析报告`
PROJECT_HEADING_RE = re.compile(r"^#\s+([\w.-]+/[\w.-]+)\s+-\s+深度分析报告\s*$")


def slice_project_analysis(content: str, project_name: str) -> str:
    """从单日完整报告的 Markdown 内容中切出单个项目段落。

    段落以 `# owner/repo - 深度分析报告` 开头，到下一个 `---` 分隔符前结束。
    """
    if not content:
        return ""

    lines = content.splitlines()
    start_idx: int | None = None
    for index, line in enumerate(lines):
        match = PROJECT_HEADING_RE.match(line.strip())
        if match and match.group(1) == project_name:
            start_idx = index
            break

    if start_idx is None:
        return ""

    end_idx = len(lines)
    for index in range(start_idx + 1, len(lines)):
        if lines[index].strip() == "---":
            end_idx = index
            break

    return "\n".join(lines[start_idx:end_idx]).strip()


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


@projects_bp.route("/project/<path:project_name>/analysis")
def get_project_analysis(project_name: str):
    """返回单个项目的 AI 深度分析切片（从当日 .md 报告中按标题切出）。"""
    decoded_project_name = decode_uri_component(project_name)
    is_valid, error_message = validate_project_name(decoded_project_name)
    if not is_valid:
        return error_response(ErrorCode.VALIDATION_ERROR, error_message, 400)

    try:
        # 1. 先从数据库查到该项目的最后分析日期
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT summary_date FROM summarized_projects WHERE name = ? LIMIT 1",
                (decoded_project_name,),
            )
            row = cursor.fetchone()
        summary_date = row[0] if row else None

        if not summary_date:
            return success_response({
                "project_name": decoded_project_name,
                "summary_date": None,
                "content": "",
                "has_analysis": False,
            })

        # 2. 读取对应日期的 .md 报告
        md_path = os.path.join(MD_DIR, f"github_trending_{summary_date}.md")
        if not os.path.exists(md_path):
            return success_response({
                "project_name": decoded_project_name,
                "summary_date": summary_date,
                "content": "",
                "has_analysis": False,
            })

        with open(md_path, "r", encoding="utf-8") as handle:
            full_content = handle.read()

        # 3. 按项目标题切片
        section = slice_project_analysis(full_content, decoded_project_name)
        return success_response({
            "project_name": decoded_project_name,
            "summary_date": summary_date,
            "content": section,
            "has_analysis": bool(section),
        })
    except Exception as exc:
        logger.error("Failed to slice project analysis %s: %s", decoded_project_name, exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve project analysis", 500)


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
