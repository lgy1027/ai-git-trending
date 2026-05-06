"""Shared helpers for route modules."""

from __future__ import annotations

import os
import re
from datetime import datetime

from flask import request

from app.database import ProjectDatabase
from config.settings import MD_DIR


REPORT_PROJECT_PATTERNS = (
    re.compile(r"(?m)^###\s+✨\s+"),
    re.compile(r"(?m)^#\s+[\w.-]+/[\w.-]+\s+-\s+深度分析报告\s*$"),
    re.compile(r"(?m)^#{2,4}\s+[\w.-]+/[\w.-]+\b"),
)


def get_client_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def validate_project_name(project_name: str | None) -> tuple[bool, str | None]:
    if not project_name:
        return False, "Project name is required"
    if len(project_name) > 200:
        return False, "Project name is too long"
    if ".." in project_name or "\x00" in project_name or "%00" in project_name:
        return False, "Invalid project name"
    if not re.match(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$", project_name):
        return False, "Invalid project name format, expected owner/repo"
    return True, None


def validate_date_string(date_str: str | None) -> tuple[bool, str | None]:
    if not date_str:
        return False, "Date is required"
    if ".." in date_str or "/" in date_str or "\\" in date_str:
        return False, "Invalid date format"
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return False, "Date must use YYYY-MM-DD"
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False, "Date does not exist"
    return True, None


def validate_format_string(format_str: str | None) -> bool:
    return format_str in {"html", "md"}


def get_report_data_from_filename(filename: str):
    try:
        date_str = filename.split("_")[-1].replace(".md", "")
        datetime.strptime(date_str, "%Y-%m-%d")
        return {
            "date": date_str,
            "path": os.path.join(MD_DIR, filename),
        }
    except (IndexError, ValueError):
        return None


def count_projects_in_report(content: str) -> int:
    if not content:
        return 0
    return max((len(pattern.findall(content)) for pattern in REPORT_PROJECT_PATTERNS), default=0)


def find_project_details(project_name: str):
    db = ProjectDatabase()
    with db._get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name, url, description, language, stars, forks, contributor_count,
                   created_at, updated_at, open_issues, watchers, summary_date
            FROM summarized_projects
            WHERE name = ?
            """,
            (project_name,),
        )
        row = cursor.fetchone()

        if row:
            return {
                "name": row[0],
                "url": row[1],
                "description": row[2],
                "language": row[3],
                "stars": row[4],
                "forks": row[5],
                "contributor_count": row[6],
                "created_at": row[7],
                "updated_at": row[8],
                "open_issues": row[9],
                "watchers": row[10],
                "summary_date": row[11],
                "analysis_status": "completed",
            }

        cursor.execute(
            """
            SELECT p.name, p.url, p.description, l.name AS language,
                   latest.full_date, latest.rank, latest.stars, latest.forks
            FROM dim_projects p
            LEFT JOIN dim_languages l ON p.language_id = l.language_id
            LEFT JOIN (
                SELECT f.project_id, d.full_date, f.rank, f.stars, f.forks
                FROM fact_trending_snapshots f
                JOIN dim_dates d ON f.date_id = d.date_id
                WHERE f.project_id = (
                    SELECT project_id FROM dim_projects WHERE name = ?
                )
                ORDER BY d.full_date DESC
                LIMIT 1
            ) latest ON p.project_id = latest.project_id
            WHERE p.name = ?
            """,
            (project_name, project_name),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "name": row[0],
            "url": row[1],
            "description": row[2],
            "language": row[3] or "Unknown",
            "stars": row[6] or 0,
            "forks": row[7] or 0,
            "contributor_count": 0,
            "created_at": "N/A",
            "updated_at": "N/A",
            "open_issues": 0,
            "watchers": 0,
            "summary_date": None,
            "analysis_status": "pending",
            "trending_date": row[4],
            "trending_rank": row[5],
            "message": "This repository has been ingested but does not have an AI analysis yet.",
        }
