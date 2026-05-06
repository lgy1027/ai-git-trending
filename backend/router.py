from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config.settings import MD_DIR, HTML_DIR
from config.logging_config import get_logger
import os
import re
from datetime import datetime, timedelta
from app.database import ProjectDatabase
from app.cache import get_rate_limiter
import urllib.parse

# 导入蓝图
from routes.projects import projects_bp as projects_bp
from routes.stats import stats_bp as stats_bp

# 创建日志记录器
logger = get_logger('router', 'INFO')

# 初始化限流器
rate_limiter = get_rate_limiter()


def get_client_ip():
    """获取客户端 IP 地址"""
    # 优先获取 X-Forwarded-For（反向代理）
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

app = Flask(__name__, static_folder='../docs/images', static_url_path='/images')

# 配置 CORS，允许所有来源
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})
db = ProjectDatabase()

# 注册蓝图
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(stats_bp, url_prefix='/api')

def get_report_data_from_filename(filename):
    try:
        date_str = filename.split('_')[-1].replace('.md', '')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return {
            "isoDate": date_str,
            "displayDate": date_obj.strftime('%Y年%m月%d日'),
            "weekday": date_obj.strftime('%A'),
            "path": os.path.join(MD_DIR, filename)
        }
    except (IndexError, ValueError):
        return None

def count_projects_in_report(content):
    """
    Count project sections across report formats.

    Older reports use headings like "### ✨ owner/repo ..."; newer reports use
    "# owner/repo - 深度分析报告". Keep the parser tolerant so metadata does not
    depend on one prompt template.
    """
    heading_patterns = [
        r'(?m)^###\s+✨\s+',
        r'(?m)^#\s+[\w.-]+/[\w.-]+\s+-\s+深度分析报告\s*$',
        r'(?m)^#{2,4}\s+[\w.-]+/[\w.-]+\b',
    ]

    return max((len(re.findall(pattern, content)) for pattern in heading_patterns), default=0)

def find_project_details(project_name):
    """Return analyzed project data when available, otherwise trending snapshot data."""
    with db._get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name, url, description, language, stars, forks, contributor_count,
                   created_at, updated_at, open_issues, watchers, summary_date
            FROM summarized_projects
            WHERE name = ?
            """,
            (project_name,)
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
                "analysis_status": "completed"
            }

        cursor.execute(
            """
            SELECT p.name, p.url, p.description, l.name as language,
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
            (project_name, project_name)
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
            "message": "此项目已抓取但尚未生成 AI 分析，只返回趋势快照信息"
        }

@app.route('/api/reports')
def get_reports():
    try:
        files = os.listdir(MD_DIR)
        md_files = sorted([f for f in files if f.endswith('.md')], reverse=True)
        
        reports = []
        for filename in md_files:
            data = get_report_data_from_filename(filename)
            if data:
                with open(data['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    project_count = count_projects_in_report(content)
                
                report = {
                    "date": data['isoDate'],
                    "project_count": project_count
                }
                reports.append(report)

        return jsonify(reports)
    except Exception as e:
        logger.error(f"Error in /api/reports: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/report/<date_str>')
def get_report_content(date_str):
    filename = f"github_trending_{date_str}.md"
    filepath = os.path.join(MD_DIR, filename)

    if not os.path.exists(filepath):
        logger.warning(f"Report not found: {filepath}")
        return jsonify({"error": "Report not found"}), 404

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        project_count = count_projects_in_report(content)
        
        report = {
            "date": date_str,
            "content": content,
            "project_count": project_count
        }
        
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error in /api/report/{date_str}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<date_str>/<format>')
def download_report(date_str, format):
    """下载报告（导出功能，带 IP 限流）"""
    client_ip = get_client_ip()

    # 检查导出限流
    allowed, remaining = rate_limiter.check_limit('export', client_ip)
    if not allowed:
        logger.warning(f"导出次数超限 - IP: {client_ip}, 日期: {date_str}")
        return jsonify({
            "error": "导出次数已达上限",
            "message": "每天最多导出 5 次，请明天再试",
            "limit": 5,
            "remaining": 0
        }), 429

    if format not in ['html', 'md']:
        return jsonify({"error": "Invalid format specified"}), 400

    dir_path = HTML_DIR if format == 'html' else MD_DIR
    filename = f"github_trending_{date_str}.{format}"

    if not os.path.exists(os.path.join(dir_path, filename)):
        logger.warning(f"Download request for non-existent file: {filename}")
        return jsonify({"error": "File not found"}), 404

    # 增加导出计数
    rate_limiter.increment('export', client_ip)
    new_remaining = rate_limiter.get_remaining('export', client_ip)

    try:
        response = send_from_directory(dir_path, filename, as_attachment=True)
        # 在响应头中返回剩余次数
        response.headers['X-RateLimit-Remaining'] = str(new_remaining)
        response.headers['X-RateLimit-Limit'] = '5'
        return response
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        return jsonify({"error": "Could not process file download"}), 500


@app.route('/api/copy/<date_str>')
def copy_report(date_str):
    """复制报告内容（带 IP 限流）"""
    client_ip = get_client_ip()

    # 检查复制限流
    allowed, remaining = rate_limiter.check_limit('copy', client_ip)
    if not allowed:
        logger.warning(f"复制次数超限 - IP: {client_ip}, 日期: {date_str}")
        return jsonify({
            "error": "复制次数已达上限",
            "message": "每天最多复制 5 次，请明天再试",
            "limit": 5,
            "remaining": 0
        }), 429

    filename = f"github_trending_{date_str}.md"
    filepath = os.path.join(MD_DIR, filename)

    if not os.path.exists(filepath):
        logger.warning(f"Copy request for non-existent file: {filename}")
        return jsonify({"error": "Report not found"}), 404

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 增加复制计数
        rate_limiter.increment('copy', client_ip)
        new_remaining = rate_limiter.get_remaining('copy', client_ip)

        response = jsonify({
            "date": date_str,
            "content": content,
            "rate_limit": {
                "limit": 5,
                "remaining": new_remaining
            }
        })
        response.headers['X-RateLimit-Remaining'] = str(new_remaining)
        response.headers['X-RateLimit-Limit'] = '5'
        return response
    except Exception as e:
        logger.error(f"Error copying file {filename}: {e}")
        return jsonify({"error": "Could not read file"}), 500


@app.route('/api/rate-limit-status')
def get_rate_limit_status():
    """获取当前 IP 的限流状态"""
    client_ip = get_client_ip()
    copy_limit = rate_limiter.get_limit('copy')
    export_limit = rate_limiter.get_limit('export')
    copy_remaining = rate_limiter.get_remaining('copy', client_ip)
    export_remaining = rate_limiter.get_remaining('export', client_ip)

    return jsonify({
        "ip": client_ip,
        "copy": {
            "limit": copy_limit,
            "remaining": copy_remaining
        },
        "export": {
            "limit": export_limit,
            "remaining": export_remaining
        }
    })


@app.route('/api/trends')
def get_trends_data():
    try:
        # Get 'days' from query parameters, default to 7
        days_str = request.args.get('days', '7')
        try:
            days = int(days_str)
            # Add some validation, e.g., allow only specific values
            allowed_days = [7, 30, 182, 365]
            if days not in allowed_days:
                # Or just cap it, for now let's stick to allowed values for simplicity
                days = 7
        except ValueError:
            days = 7

        # Import here to avoid circular imports
        from app.analyzer import analyze_trends
        
        logger.info(f"📊 Received trends request for {days} days.")
        trends_data = analyze_trends(days=days)
        return jsonify(trends_data)
    except Exception as e:
        logger.error(f"Error in /api/trends: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
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
            # 设置基准值和最低分数，确保即使数据不足也能有合理的活跃度显示
            base_contributors = 10
            base_stars = 100
            base_forks = 50
            
            # 为每个指标设置最低分数，确保活跃度不会显示为0%
            min_contributors_score = 5
            min_stars_score = 10
            min_forks_score = 5
            
            # 计算各项指标的归一化值，并应用最低分数
            contributors_score = max(min_contributors_score, min(100, (avg_contributors / base_contributors) * 25))
            stars_score = max(min_stars_score, min(100, (avg_stars / base_stars) * 40))
            forks_score = max(min_forks_score, min(100, (avg_forks / base_forks) * 35))
            
            # 综合计算活跃度分数
            activity_score = round(contributors_score + stars_score + forks_score)
            
            # 确保活跃度分数在合理范围内
            activity_score = max(20, min(100, activity_score))  # 设置最低20%的活跃度分数
            
            stats = {
                "totalReports": total_reports,
                "totalProjects": total_projects,
                "topLanguage": top_language,
                "weeklyNew": weekly_new,
                "totalForks": f"{total_forks:,}", # Formatted with commas
                "avgContributors": round(avg_contributors, 1),
                "activityScore": activity_score
            }
            return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/language-distribution')
def get_language_distribution():
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取语言分布数据
            cursor.execute("SELECT language, COUNT(*) as count FROM summarized_projects WHERE language != 'N/A' AND language IS NOT NULL GROUP BY language ORDER BY count DESC LIMIT 10")
            language_rows = cursor.fetchall()
            
            # 计算总项目数（排除N/A语言）
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE language != 'N/A' AND language IS NOT NULL")
            total_valid_projects = cursor.fetchone()[0] or 1  # 避免除以零
            
            # 格式化语言分布数据
            language_distribution = []
            for language, count in language_rows:
                percentage = round((count / total_valid_projects) * 100)
                # 为每种语言分配一个颜色类
                color_classes = {
                    'JavaScript': 'bg-gradient-to-r from-yellow-500 to-yellow-600',
                    'Python': 'bg-gradient-to-r from-green-500 to-green-600',
                    'TypeScript': 'bg-gradient-to-r from-blue-500 to-blue-600',
                    'Go': 'bg-gradient-to-r from-cyan-500 to-cyan-600',
                    'Rust': 'bg-gradient-to-r from-orange-500 to-orange-600',
                    'Java': 'bg-gradient-to-r from-red-500 to-red-600',
                    'C++': 'bg-gradient-to-r from-blue-500 to-blue-600',
                    'C#': 'bg-gradient-to-r from-purple-500 to-purple-600',
                    'PHP': 'bg-gradient-to-r from-blue-500 to-blue-600',
                    'Ruby': 'bg-gradient-to-r from-red-500 to-red-600'
                }
                color_class = color_classes.get(language, 'bg-gradient-to-r from-gray-500 to-gray-600')
                
                language_distribution.append({
                    "name": language,
                    "count": count,
                    "percentage": percentage,
                    "colorClass": color_class
                })
            
            return jsonify(language_distribution)
    except Exception as e:
        logger.error(f"Error in /api/language-distribution: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/trend-data')
def get_trend_data():
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取总项目数
            cursor.execute("SELECT COUNT(*) FROM summarized_projects")
            total_projects = cursor.fetchone()[0] or 0
            
            # 获取本周新增项目数
            one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE summary_date >= ?", (one_week_ago,))
            weekly_new = cursor.fetchone()[0] or 0
            
            # 获取活跃项目数（过去一周有更新的项目）
            one_week_ago_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE updated_at >= ?", (one_week_ago_date,))
            active_projects = cursor.fetchone()[0] or 0
            
            # 获取热门项目数（stars > 1000）
            cursor.execute("SELECT COUNT(*) FROM summarized_projects WHERE stars > 1000")
            popular_projects = cursor.fetchone()[0] or 0
            
            # 获取趋势项目数（最近获得较多stars的项目）
            # 这里简化处理，实际应根据趋势计算
            trend_projects = max(0, int(total_projects * 0.05))
            
            # 计算变化趋势（这里简化处理）
            trend_data = [
                {"label": "新项目", "value": weekly_new, "change": 1, "colorClass": "bg-green-400"},
                {"label": "活跃项目", "value": active_projects, "change": 1, "colorClass": "bg-blue-400"},
                {"label": "热门项目", "value": popular_projects, "change": 0, "colorClass": "bg-purple-400"},
                {"label": "趋势项目", "value": trend_projects, "change": -1, "colorClass": "bg-pink-400"}
            ]
            
            return jsonify(trend_data)
    except Exception as e:
        logger.error(f"Error in /api/trend-data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project_name>')
def get_project_details(project_name):
    """获取单个项目的详细信息"""
    try:
        # 解码URL编码的项目名称
        decoded_project_name = decodeURIComponent(project_name)
        logger.info(f"获取项目详情: {decoded_project_name}")

        project = find_project_details(decoded_project_name)
        if project:
            return jsonify(project)

        logger.warning(f"项目未找到: {decoded_project_name}")
        return jsonify({"error": "Project not found", "project_name": decoded_project_name}), 404
    except Exception as e:
        logger.error(f"获取项目详情错误: {e}")
        return jsonify({"error": str(e), "project_name": project_name}), 500

@app.route('/api/project', methods=['GET', 'POST'])
def get_project_details_api():
    """通过GET或POST请求获取单个项目的详细信息，GET请求从查询参数获取，POST请求从请求体获取"""
    try:
        if request.method == 'GET':
            # 从查询参数中获取项目名称
            project_name = request.args.get('name') or request.args.get('project_name')
            if not project_name:
                logger.warning("GET请求缺少name查询参数")
                return jsonify({"error": "Missing name parameter in query string"}), 400
        else:  # POST请求
            # 从请求体中获取项目名称
            data = request.get_json()
            if not data or 'project_name' not in data:
                logger.warning("POST请求缺少project_name参数")
                return jsonify({"error": "Missing project_name parameter in request body"}), 400
            
            project_name = data['project_name']
        logger.info(f"通过{request.method}请求获取项目详情: {project_name}")

        project = find_project_details(project_name)
        if project:
            return jsonify(project)

        logger.warning(f"项目未找到: {project_name}")
        return jsonify({"error": "Project not found", "project_name": project_name}), 404
    except Exception as e:
        logger.error(f"通过POST请求获取项目详情错误: {e}")
        return jsonify({"error": str(e), "project_name": project_name if 'project_name' in locals() else "N/A"}), 500

# 辅助函数：解码URI组件
def decodeURIComponent(encoded_str):
    """解码URI编码的字符串，适配前端encodeURIComponent的编码"""
    return urllib.parse.unquote(encoded_str)
