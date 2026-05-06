"""
Stats API routes.
"""

import os
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, make_response, request

stats_bp = Blueprint('stats', __name__)

from app.database import ProjectDatabase
from app.cache import get_cache, generate_cache_key
from app.response import success_response, error_response, ErrorCode
from config.settings import MD_DIR, STATS_BASE_CONTRIBUTORS, STATS_BASE_STARS, STATS_BASE_FORKS, STATS_MIN_CONTRIBUTORS_SCORE, STATS_MIN_STARS_SCORE, STATS_MIN_FORKS_SCORE
from config.logging_config import get_logger

logger = get_logger('stats', 'INFO')

db = ProjectDatabase()


@stats_bp.route('/stats')
def get_stats():
    """获取统计数据（带缓存）"""
    # 默认缓存 5 分钟
    CACHE_TTL = 300

    # 检查缓存
    cache = get_cache()
    cache_key = generate_cache_key('/api/stats')

    # 尝试从缓存获取
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        response = make_response(cached_result['body'])
        response.headers['Content-Type'] = 'application/json'
        response.headers['X-Cache'] = 'HIT'
        return response

    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM summarized_projects")
            total_projects = cursor.fetchone()[0]

            cursor.execute("SELECT language, COUNT(*) as count FROM summarized_projects WHERE language != 'N/A' AND language IS NOT NULL GROUP BY language ORDER BY count DESC LIMIT 1")
            top_lang_row = cursor.fetchone()
            top_language = top_lang_row[0] if top_lang_row else "N/A"

            one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE summary_date >= ?", (one_week_ago,))
            weekly_new = cursor.fetchone()[0]

            total_reports = len([f for f in os.listdir(MD_DIR) if f.endswith('.md')])

            # New Stats
            cursor.execute("SELECT SUM(forks) FROM summarized_projects")
            total_forks = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(contributor_count) FROM summarized_projects WHERE contributor_count != 'N/A'")
            avg_contributors = cursor.fetchone()[0] or 0

            # 计算活跃度分数 - 基于贡献者数量、stars和forks等指标
            cursor.execute("SELECT AVG(contributor_count) FROM summarized_projects WHERE contributor_count != 'N/A'")
            avg_contributors = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(stars) FROM summarized_projects")
            avg_stars = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(forks) FROM summarized_projects")
            avg_forks = cursor.fetchone()[0] or 0

            # 改进的活跃度计算公式
            base_contributors = STATS_BASE_CONTRIBUTORS
            base_stars = STATS_BASE_STARS
            base_forks = STATS_BASE_FORKS

            min_contributors_score = STATS_MIN_CONTRIBUTORS_SCORE
            min_stars_score = STATS_MIN_STARS_SCORE
            min_forks_score = STATS_MIN_FORKS_SCORE

            contributors_score = max(min_contributors_score, min(100, (avg_contributors / base_contributors) * 25))
            stars_score = max(min_stars_score, min(100, (avg_stars / base_stars) * 40))
            forks_score = max(min_forks_score, min(100, (avg_forks / base_forks) * 35))

            activity_score = round(contributors_score + stars_score + forks_score)
            activity_score = max(20, min(100, activity_score))

            # 按活跃度分类统计
            now = datetime.now()
            seven_days_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
            ninety_days_ago = (now - timedelta(days=90)).strftime('%Y-%m-%d')

            # 活跃: 7天内更新
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE updated_at >= ?", (seven_days_ago,))
            recently_active = cursor.fetchone()[0]

            # 稳定: 7-90天未更新
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE updated_at < ? AND updated_at >= ?", (seven_days_ago, ninety_days_ago,))
            stable = cursor.fetchone()[0]

            # 需关注: 90天以上未更新
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE updated_at < ? OR updated_at = 'N/A' OR updated_at IS NULL", (ninety_days_ago,))
            needs_attention = cursor.fetchone()[0]

            stats = {
                "totalReports": total_reports,
                "totalProjects": total_projects,
                "weeklyNew": weekly_new,
                "totalForks": total_forks,
                "avgStars": round(avg_stars, 1),
                "avgForks": round(avg_forks, 1),
                "avgContributors": round(avg_contributors, 1),
                "topLanguage": top_language,
                "activityScore": activity_score,
                "activityBreakdown": {
                    "recentlyActive": recently_active,
                    "stable": stable,
                    "needsAttention": needs_attention
                }
            }

            # 缓存结果
            import json
            cache.set(cache_key, {'body': json.dumps(stats)}, CACHE_TTL)

            response = make_response(jsonify(stats))
            response.headers['X-Cache'] = 'MISS'
            return response
    except Exception as e:
        logger.error(f"获取统计数据错误: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e), 500)


@stats_bp.route('/tech-domains')
def get_tech_domains():
    """获取所有可用的技术领域分类"""
    # 预定义的 15 个技术领域
    predefined_domains = [
        'AI/ML', 'LLM Apps', 'Web', 'Frontend', 'Mobile',
        'DevOps', 'Data Science', 'Database', 'Tools',
        'Security', 'Blockchain', 'Gaming', 'OS', 'IoT', 'Other'
    ]

    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tech_domain, COUNT(*) as count
                FROM summarized_projects
                WHERE tech_domain IS NOT NULL AND tech_domain != ''
                GROUP BY tech_domain
                ORDER BY count DESC
            """)
            rows = cursor.fetchall()

            # 构建已有领域的计数映射
            existing_domains = {row[0]: row[1] for row in rows}

            # 返回所有预定义领域，count 为 0 表示没有数据
            domains = [
                {"name": domain, "count": existing_domains.get(domain, 0)}
                for domain in predefined_domains
            ]

            return success_response(domains)
    except Exception as e:
        logger.error(f"获取技术领域错误: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e), 500)


@stats_bp.route('/language-distribution')
def get_language_distribution():
    """获取编程语言分布统计"""
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM summarized_projects
                WHERE language IS NOT NULL AND language != 'N/A' AND language != ''
                GROUP BY language
                ORDER BY count DESC
                LIMIT 10
            """)
            rows = cursor.fetchall()

            languages = [{"name": row[0], "count": row[1]} for row in rows]

            return success_response(languages)
    except Exception as e:
        logger.error(f"获取语言分布错误: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e), 500)


@stats_bp.route('/project-trend')
def get_project_trend():
    """获取项目趋势（最近N天的每日项目数）"""
    try:
        days = request.args.get('days', 7, type=int)
        if days > 30:
            days = 30

        with db._get_connection() as conn:
            cursor = conn.cursor()

            # 获取最近days天的数据
            cursor.execute(f"""
                SELECT summary_date, COUNT(*) as count
                FROM summarized_projects
                WHERE summary_date >= date('now', '-{days} days')
                GROUP BY summary_date
                ORDER BY summary_date ASC
            """)
            rows = cursor.fetchall()

            trend = [{"date": row[0], "count": row[1]} for row in rows]

            return success_response(trend)
    except Exception as e:
        logger.error(f"获取项目趋势错误: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e), 500)
