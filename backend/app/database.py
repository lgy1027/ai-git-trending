import sqlite3
from config.settings import DB_PATH
from datetime import date
from config.logging_config import get_logger

# 创建日志记录器
logger = get_logger('database', 'INFO')

# 白名单：允许的表名和列名
ALLOWED_TABLES = {'dim_languages', 'dim_tags'}
ALLOWED_COLUMNS = {'language', 'tag'}

class ProjectDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_schema()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10) # Add timeout to reduce locking issues
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_schema(self):
        """
        创建数据库架构
        
        数据模型设计说明：
        1. 星型模型 (dim_* + fact_*) - 用于历史趋势分析
           - dim_languages: 语言维度
           - dim_tags: 标签维度  
           - dim_projects: 项目维度
           - dim_dates: 日期维度
           - fact_trending_snapshots: 趋势快照事实表
           - assoc_project_tags: 项目-标签关联表
        
        2. 汇总表 (summarized_projects) - 用于快速查询展示
           - 存储最新的项目汇总信息
           - 适合列表查询、搜索筛选
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # ==================== 维度表 ====================
                cursor.execute("CREATE TABLE IF NOT EXISTS dim_languages (language_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
                cursor.execute("CREATE TABLE IF NOT EXISTS dim_tags (tag_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dim_projects (
                        project_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, url TEXT,
                        description TEXT, language_id INTEGER,
                        FOREIGN KEY (language_id) REFERENCES dim_languages (language_id)
                    )""")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dim_dates (
                        date_id INTEGER PRIMARY KEY, full_date DATE NOT NULL UNIQUE, year INTEGER,
                        month INTEGER, day INTEGER, weekday INTEGER, week_of_year INTEGER
                    )""")
                
                # ==================== 关联表 ====================
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS assoc_project_tags (
                        project_id INTEGER, tag_id INTEGER, PRIMARY KEY (project_id, tag_id),
                        FOREIGN KEY (project_id) REFERENCES dim_projects (project_id),
                        FOREIGN KEY (tag_id) REFERENCES dim_tags (tag_id)
                    )""")
                
                # ==================== 事实表 ====================
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fact_trending_snapshots (
                        snapshot_id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, date_id INTEGER NOT NULL,
                        rank INTEGER NOT NULL, stars INTEGER, forks INTEGER,
                        UNIQUE(project_id, date_id),
                        FOREIGN KEY (project_id) REFERENCES dim_projects (project_id),
                        FOREIGN KEY (date_id) REFERENCES dim_dates (date_id)
                    )""")
                
                # ==================== 汇总表 ====================
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS summarized_projects (
                        name TEXT PRIMARY KEY, url TEXT, description TEXT, language TEXT, stars INTEGER,
                        forks INTEGER, contributor_count INTEGER, created_at TEXT, updated_at TEXT,
                        open_issues INTEGER, watchers INTEGER, summary_date TEXT NOT NULL,
                        tech_domain TEXT
                    )""")
                
                # ==================== 索引优化 ====================
                # summarized_projects 表索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_summarized_language ON summarized_projects(language)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_summarized_summary_date ON summarized_projects(summary_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_summarized_stars ON summarized_projects(stars)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_summarized_forks ON summarized_projects(forks)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_summarized_tech_domain ON summarized_projects(tech_domain)")
                
                # 事实表索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_date_id ON fact_trending_snapshots(date_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_project_id ON fact_trending_snapshots(project_id)")
                
                # 维度表索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_dim_projects_language ON dim_projects(language_id)")

                # ==================== IP 限流表（永久限制）====================
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ip_rate_limits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip_address TEXT NOT NULL,
                        action TEXT NOT NULL,
                        count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ip_address, action)
                    )""")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ip_rate_limits_lookup ON ip_rate_limits(ip_address, action)")

                conn.commit()

                # 迁移：添加 tech_domain 列（如果不存在）
                try:
                    cursor.execute("SELECT tech_domain FROM summarized_projects LIMIT 1")
                except sqlite3.OperationalError:
                    # 列不存在，添加它
                    cursor.execute("ALTER TABLE summarized_projects ADD COLUMN tech_domain TEXT")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_summarized_tech_domain ON summarized_projects(tech_domain)")
                    conn.commit()
                    logger.info("✅ Migration: Added tech_domain column")
        except sqlite3.Error as e:
            logger.error(f"❌ Database error (_create_schema): {e}")

    # --- Refactored Dimension Helpers to use a passed cursor ---

    def _get_or_create_dimension_id(self, cursor, table, column, value):
        """安全地获取或创建维度ID，使用白名单防止SQL注入"""
        # 验证表名
        if table not in ALLOWED_TABLES:
            raise ValueError(f"Invalid table: {table}. Allowed tables: {ALLOWED_TABLES}")
        
        # 验证列名
        if column not in ALLOWED_COLUMNS:
            raise ValueError(f"Invalid column: {column}. Allowed columns: {ALLOWED_COLUMNS}")
        
        cursor.execute(f"SELECT {column}_id FROM {table} WHERE name = ?", (value,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            cursor.execute(f"INSERT INTO {table} (name) VALUES (?)", (value,))
            return cursor.lastrowid

    def get_or_create_language_id(self, cursor, language_name):
        if not language_name or language_name == 'N/A':
            return None
        return self._get_or_create_dimension_id(cursor, 'dim_languages', 'language', language_name)

    def get_or_create_tag_id(self, cursor, tag_name):
        return self._get_or_create_dimension_id(cursor, 'dim_tags', 'tag', tag_name)

    def get_or_create_date_id(self, cursor, date_obj):
        date_id = int(date_obj.strftime('%Y%m%d'))
        cursor.execute("SELECT date_id FROM dim_dates WHERE date_id = ?", (date_id,))
        if cursor.fetchone():
            return date_id
        else:
            cursor.execute("INSERT INTO dim_dates (date_id, full_date, year, month, day, weekday, week_of_year) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (date_id, date_obj, date_obj.year, date_obj.month, date_obj.day, date_obj.weekday(), date_obj.isocalendar()[1]))
            return date_id

    def get_or_create_project_id(self, cursor, project_data):
        cursor.execute("SELECT project_id FROM dim_projects WHERE name = ?", (project_data['name'],))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            lang_id = self.get_or_create_language_id(cursor, project_data.get('language'))
            cursor.execute("INSERT INTO dim_projects (name, url, description, language_id) VALUES (?, ?, ?, ?)",
                           (project_data['name'], project_data.get('url'), project_data.get('description'), lang_id))
            project_id = cursor.lastrowid
            
            tag_names = project_data.get('tags', [])
            for tag_name in tag_names:
                tag_id = self.get_or_create_tag_id(cursor, tag_name)
                cursor.execute("INSERT OR IGNORE INTO assoc_project_tags (project_id, tag_id) VALUES (?, ?)", (project_id, tag_id))
            return project_id

    # --- Main method now manages the connection for the whole transaction ---

    def add_trending_snapshots(self, projects_data, snapshot_date):
        """
        Adds a batch of trending snapshots in a single transaction.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                date_id = self.get_or_create_date_id(cursor, snapshot_date)
                
                for project_data in projects_data:
                    project_id = self.get_or_create_project_id(cursor, project_data)
                    cursor.execute(
                        """INSERT OR IGNORE INTO fact_trending_snapshots 
                           (project_id, date_id, rank, stars, forks) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            project_id, date_id, project_data['rank'],
                            project_data.get('stars', 0), project_data.get('forks', 0)
                        )
                    )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"❌ Database error (add_trending_snapshots): {e}")


    # --- Methods for the old reporting feature (to keep it working) ---
    def get_all_summarized_project_names(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM summarized_projects")
                return {row[0] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logger.error(f"❌ Database error (get_all_summarized_project_names): {e}")
            return set()

    def add_summarized_project(self, project):
        if not project: return
        today_str = date.today().isoformat()
        
        # Helper to safely convert 'N/A' or other non-integers to 0
        def safe_int(value, default=0):
            if value == 'N/A':
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        project_data = (
            project.get('name'),
            project.get('url'),
            project.get('description', 'N/A'),
            project.get('language', 'N/A'),
            safe_int(project.get('stars')),
            safe_int(project.get('forks')),
            safe_int(project.get('contributor_count')),
            project.get('created_at', 'N/A'),
            project.get('updated_at', 'N/A'),
            safe_int(project.get('open_issues')),
            safe_int(project.get('watchers')),
            today_str,
            project.get('tech_domain', 'Other')  # 技术领域，默认 Other
        )
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO summarized_projects
                       (name, url, description, language, stars, forks, contributor_count,
                        created_at, updated_at, open_issues, watchers, summary_date, tech_domain)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    project_data
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"❌ Database error (add_summarized_project): {e}")

    # ==================== IP 限流操作 ====================

    def get_rate_limit_count(self, ip_address: str, action: str) -> int:
        """获取指定 IP 和操作的计数（永久限制）"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT count FROM ip_rate_limits WHERE ip_address = ? AND action = ?",
                    (ip_address, action)
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"❌ Database error (get_rate_limit_count): {e}")
            return 0

    def increment_rate_limit(self, ip_address: str, action: str, max_count: int = 5) -> tuple[bool, int]:
        """
        增加限流计数，返回 (是否允许, 剩余次数)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 先查询当前计数
                cursor.execute(
                    "SELECT count FROM ip_rate_limits WHERE ip_address = ? AND action = ?",
                    (ip_address, action)
                )
                result = cursor.fetchone()
                current_count = result[0] if result else 0

                if current_count >= max_count:
                    return False, max_count - current_count

                # 增加计数
                new_count = current_count + 1
                cursor.execute(
                    """INSERT INTO ip_rate_limits (ip_address, action, count)
                       VALUES (?, ?, ?)
                       ON CONFLICT(ip_address, action) DO UPDATE SET count = ?""",
                    (ip_address, action, new_count, new_count)
                )
                conn.commit()
                return True, max_count - new_count
        except sqlite3.Error as e:
            logger.error(f"❌ Database error (increment_rate_limit): {e}")
            return True, max_count  # 出错时默认允许

    def get_all_rate_limits_for_ip(self, ip_address: str) -> dict:
        """获取指定 IP 的所有限流信息"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT action, count FROM ip_rate_limits WHERE ip_address = ?",
                    (ip_address,)
                )
                result = {row[0]: row[1] for row in cursor.fetchall()}
                return result
        except sqlite3.Error as e:
            logger.error(f"❌ Database error (get_all_rate_limits_for_ip): {e}")
            return {}
