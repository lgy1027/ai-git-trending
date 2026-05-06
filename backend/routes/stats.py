"""Statistics-related API routes."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from flask import Blueprint, make_response, request

from app.cache import generate_cache_key, get_cache
from app.database import ProjectDatabase
from app.response import ErrorCode, error_response, success_response
from config.logging_config import get_logger
from config.settings import (
    MD_DIR,
    STATS_BASE_CONTRIBUTORS,
    STATS_BASE_FORKS,
    STATS_BASE_STARS,
    STATS_MIN_CONTRIBUTORS_SCORE,
    STATS_MIN_FORKS_SCORE,
    STATS_MIN_STARS_SCORE,
)

stats_bp = Blueprint("stats", __name__)
logger = get_logger("stats", "INFO")
db = ProjectDatabase()


@stats_bp.route("/stats")
def get_stats():
    cache = get_cache()
    cache_key = generate_cache_key("/api/stats")
    cached = cache.get(cache_key)
    if cached is not None:
        response = make_response(cached)
        response.headers["Content-Type"] = "application/json"
        response.headers["X-Cache"] = "HIT"
        return response

    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM summarized_projects")
            total_projects = cursor.fetchone()[0] or 0

            cursor.execute(
                """
                SELECT language, COUNT(*) AS count
                FROM summarized_projects
                WHERE language IS NOT NULL AND language != '' AND language != 'N/A'
                GROUP BY language
                ORDER BY count DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            top_language = row[0] if row else "N/A"

            one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE summary_date >= ?", (one_week_ago,))
            weekly_new = cursor.fetchone()[0] or 0

            total_reports = len([name for name in os.listdir(MD_DIR) if name.endswith(".md")])

            cursor.execute("SELECT SUM(forks) FROM summarized_projects")
            total_forks = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(contributor_count) FROM summarized_projects WHERE contributor_count != 'N/A'")
            avg_contributors = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(stars) FROM summarized_projects")
            avg_stars = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(forks) FROM summarized_projects")
            avg_forks = cursor.fetchone()[0] or 0

            contributors_score = max(
                STATS_MIN_CONTRIBUTORS_SCORE,
                min(100, (avg_contributors / STATS_BASE_CONTRIBUTORS) * 25),
            )
            stars_score = max(
                STATS_MIN_STARS_SCORE,
                min(100, (avg_stars / STATS_BASE_STARS) * 40),
            )
            forks_score = max(
                STATS_MIN_FORKS_SCORE,
                min(100, (avg_forks / STATS_BASE_FORKS) * 35),
            )
            activity_score = max(20, min(100, round(contributors_score + stars_score + forks_score)))

            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE updated_at >= ?", (seven_days_ago,))
            recently_active = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT COUNT(*) FROM summarized_projects WHERE updated_at < ? AND updated_at >= ?",
                (seven_days_ago, ninety_days_ago),
            )
            stable = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT COUNT(*) FROM summarized_projects WHERE updated_at < ? OR updated_at = 'N/A' OR updated_at IS NULL",
                (ninety_days_ago,),
            )
            needs_attention = cursor.fetchone()[0] or 0

        response = success_response(
            {
                "totalReports": total_reports,
                "totalProjects": total_projects,
                "topLanguage": top_language,
                "weeklyNew": weekly_new,
                "totalForks": f"{total_forks:,}",
                "avgContributors": round(avg_contributors, 1),
                "activityScore": activity_score,
                "activityBreakdown": {
                    "recentlyActive": recently_active,
                    "stable": stable,
                    "needsAttention": needs_attention,
                },
            }
        )
        response.headers["X-Cache"] = "MISS"
        cache.set(cache_key, response.get_data(as_text=True), 300)
        return response
    except Exception as exc:
        logger.error("Failed to compute stats: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve stats", 500)


@stats_bp.route("/tech-domains")
def get_tech_domains():
    predefined_domains = [
        "AI/ML",
        "LLM Apps",
        "Web",
        "Frontend",
        "Mobile",
        "DevOps",
        "Data Science",
        "Database",
        "Tools",
        "Security",
        "Blockchain",
        "Gaming",
        "OS",
        "IoT",
        "Other",
    ]

    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT tech_domain, COUNT(*) AS count
                FROM summarized_projects
                WHERE tech_domain IS NOT NULL AND tech_domain != ''
                GROUP BY tech_domain
                ORDER BY count DESC
                """
            )
            rows = cursor.fetchall()

        existing = {row[0]: row[1] for row in rows}
        data = [{"name": domain, "count": existing.get(domain, 0)} for domain in predefined_domains]
        return success_response(data)
    except Exception as exc:
        logger.error("Failed to retrieve tech domains: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve tech domains", 500)


@stats_bp.route("/language-distribution")
def get_language_distribution():
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT language, COUNT(*) AS count
                FROM summarized_projects
                WHERE language IS NOT NULL AND language != '' AND language != 'N/A'
                GROUP BY language
                ORDER BY count DESC
                LIMIT 10
                """
            )
            rows = cursor.fetchall()

        return success_response([{"name": row[0], "count": row[1]} for row in rows])
    except Exception as exc:
        logger.error("Failed to retrieve language distribution: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve language distribution", 500)


@stats_bp.route("/project-trend")
def get_project_trend():
    days = min(request.args.get("days", 7, type=int) or 7, 30)
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT summary_date, COUNT(*) AS count
                FROM summarized_projects
                WHERE summary_date >= date('now', '-{days} days')
                GROUP BY summary_date
                ORDER BY summary_date ASC
                """
            )
            rows = cursor.fetchall()
        return success_response([{"date": row[0], "count": row[1]} for row in rows])
    except Exception as exc:
        logger.error("Failed to retrieve project trend: %s", exc)
        return error_response(ErrorCode.INTERNAL_ERROR, "Failed to retrieve project trend", 500)
