from datetime import date, timedelta
from config.logging_config import get_logger
from app.database import ProjectDatabase
from config.categories import TECH_DOMAINS

logger = get_logger('analyzer', 'INFO')

def analyze_trends(days=7):
    """Analyzes trending data"""
    logger.info(f"分析最近{days}天的趋势数据")
    db = ProjectDatabase()
    conn = db._get_connection()
    cursor = conn.cursor()

    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # 最频繁项目查询
    sql_most_frequent = """
    SELECT
        p.name,
        MAX(COALESCE(sp.url, p.url)) as url,
        MAX(COALESCE(sp.description, p.description)) as description,
        MAX(COALESCE(sp.language, l.name, 'Unknown')) as language,
        COUNT(f.snapshot_id) as count,
        AVG(f.stars) as avg_stars,
        MAX(sp.stars) as stars,
        MAX(sp.forks) as forks,
        MAX(sp.contributor_count) as contributor_count,
        MAX(sp.created_at) as created_at,
        MAX(sp.updated_at) as updated_at,
        MAX(sp.open_issues) as open_issues,
        MAX(sp.watchers) as watchers
    FROM fact_trending_snapshots f
    JOIN dim_projects p ON f.project_id = p.project_id
    JOIN dim_dates d ON f.date_id = d.date_id
    LEFT JOIN dim_languages l ON p.language_id = l.language_id
    LEFT JOIN summarized_projects sp ON p.name = sp.name
    WHERE d.full_date BETWEEN ? AND ?
    GROUP BY p.name
    ORDER BY count DESC
    LIMIT 10"""
    
    cursor.execute(sql_most_frequent, (start_date.isoformat(), end_date.isoformat()))
    most_frequent_projects_raw = cursor.fetchall()
    
    most_frequent_projects = [
        {
            "name": row[0],
            "url": row[1],
            "description": row[2][:100] + "..." if row[2] and len(row[2]) > 100 else row[2],
            "language": row[3],
            "count": row[4],
            "avg_stars": int(row[5]) if row[5] else 0,
            "stars": row[6] if row[6] is not None else (int(row[5]) if row[5] else 0),
            "forks": row[7] if row[7] is not None else 0,
            "contributor_count": row[8] if row[8] is not None else 0,
            "created_at": row[9] if row[9] is not None else end_date.isoformat(),
            "updated_at": row[10] if row[10] is not None else end_date.isoformat(),
            "open_issues": row[11] if row[11] is not None else 0,
            "watchers": row[12] if row[12] is not None else 0
        }
        for row in most_frequent_projects_raw
    ]
    
    # 最频繁语言查询
    sql_languages = "SELECT l.name, COUNT(f.snapshot_id) as count FROM fact_trending_snapshots f JOIN dim_projects p ON f.project_id = p.project_id JOIN dim_languages l ON p.language_id = l.language_id JOIN dim_dates d ON f.date_id = d.date_id WHERE d.full_date BETWEEN ? AND ? AND l.name IS NOT NULL GROUP BY l.name ORDER BY count DESC LIMIT 10"
    
    cursor.execute(sql_languages, (start_date.isoformat(), end_date.isoformat()))
    most_frequent_languages = cursor.fetchall()
    
    # 上升项目查询
    sql_surging = """
    WITH StarHistory AS ( \
        SELECT  \
            f.project_id,\
            p.name,\
            p.url,\
            p.description,\
            l.name as language,\
            MIN(d.full_date) as first_day,\
            MAX(d.full_date) as last_day,\
            SUM(CASE WHEN d.full_date = (SELECT MIN(d2.full_date) FROM dim_dates d2 JOIN fact_trending_snapshots f2 ON d2.date_id = f2.date_id WHERE f2.project_id = f.project_id AND d2.full_date BETWEEN ? AND ?) THEN f.stars END) as start_stars,\
            SUM(CASE WHEN d.full_date = (SELECT MAX(d2.full_date) FROM dim_dates d2 JOIN fact_trending_snapshots f2 ON d2.date_id = f2.date_id WHERE f2.project_id = f.project_id AND d2.full_date BETWEEN ? AND ?) THEN f.stars END) as end_stars\
        FROM fact_trending_snapshots f\
        JOIN dim_projects p ON f.project_id = p.project_id\
        LEFT JOIN dim_languages l ON p.language_id = l.language_id\
        JOIN dim_dates d ON f.date_id = d.date_id\
        WHERE d.full_date BETWEEN ? AND ?\
        GROUP BY f.project_id, p.name, p.url, p.description, l.name\
        HAVING COUNT(f.snapshot_id) > 1\
    )\
    SELECT \
        name,\
        url,\
        description,\
        language,\
        (end_stars - start_stars) as star_increase,\
        start_stars,\
        end_stars\
    FROM StarHistory\
    WHERE star_increase > 50 \
    ORDER BY star_increase DESC\
    LIMIT 10"""
    
    cursor.execute(sql_surging, (start_date.isoformat(), end_date.isoformat(), start_date.isoformat(), end_date.isoformat(), start_date.isoformat(), end_date.isoformat()))
    surging_projects_raw = cursor.fetchall()
    
    surging_projects = [
        {
            "name": row[0], 
            "url": row[1], 
            "description": row[2][:100] + "..." if row[2] and len(row[2]) > 100 else row[2],
            "language": row[3] or "Unknown",
            "star_increase": row[4], 
            "start_stars": row[5], 
            "end_stars": row[6]
        }
        for row in surging_projects_raw
    ]
    
    conn.close()

    logger.info(f"趋势分析完成，发现{len(most_frequent_projects)}个热门项目，{len(most_frequent_languages)}种热门语言，{len(surging_projects)}个快速增长项目")

    # 技术领域数据：从真实 LLM 归类结果统计（summarized_projects.tech_domain），
    # 过滤出当前时间窗口内有 summary_date 记录的项目，按预设 15 分类输出。
    domain_rows = {}
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT tech_domain, COUNT(*) AS count
                FROM summarized_projects
                WHERE summary_date BETWEEN ? AND ?
                  AND tech_domain IS NOT NULL AND tech_domain != ''
                GROUP BY tech_domain
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            domain_rows = {row[0]: row[1] for row in cursor.fetchall()}
    except Exception as exc:
        logger.error("Failed to load tech domain distribution: %s", exc)

    tech_domains_total = sum(domain_rows.values())
    tech_domains = [
        {
            "name": domain,
            "count": domain_rows.get(domain, 0),
            "percentage": round((domain_rows.get(domain, 0) / tech_domains_total) * 100) if tech_domains_total else 0,
        }
        for domain in TECH_DOMAINS
        if domain_rows.get(domain, 0) > 0
    ]
    tech_domains.sort(key=lambda d: d["count"], reverse=True)

    return {
        "time_window_days": days,
        "topProjects": most_frequent_projects,
        "programmingLanguages": most_frequent_languages,
        "techDomains": tech_domains,
        "surgingProjects": surging_projects,
        "most_frequent_projects": most_frequent_projects,
        "most_frequent_languages": most_frequent_languages,
    }

def get_trend_by_tag(tag_name, days=30):
    """Get trend for a specific tag"""
    logger.info(f"分析标签'{tag_name}'最近{days}天的趋势")
    db = ProjectDatabase()
    conn = db._get_connection()
    cursor = conn.cursor()

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    sql_tag = "SELECT d.full_date, COUNT(DISTINCT f.project_id) FROM fact_trending_snapshots f JOIN dim_dates d ON f.date_id = d.date_id JOIN assoc_project_tags apt ON f.project_id = apt.project_id JOIN dim_tags t ON apt.tag_id = t.tag_id WHERE t.name = ? AND d.full_date BETWEEN ? AND ? GROUP BY d.full_date ORDER BY d.full_date ASC"
    
    cursor.execute(sql_tag, (tag_name, start_date.isoformat(), end_date.isoformat()))
    
    data = cursor.fetchall()
    conn.close()
    
    logger.info(f"标签'{tag_name}'的趋势分析完成，共{len(data)}个数据点")
    return data
