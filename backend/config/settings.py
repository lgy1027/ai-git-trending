"""Runtime configuration for the backend service."""

from __future__ import annotations

import os

from dotenv import load_dotenv


BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", 3))
LLM_RETRY_DELAY = int(os.getenv("LLM_RETRY_DELAY", 1))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 60))

SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")
NUM_PROJECTS_TO_SUMMARIZE = int(os.getenv("NUM_PROJECTS_TO_SUMMARIZE", 8))
MAX_PROJECTS_TO_SCRAPE = int(os.getenv("MAX_PROJECTS_TO_SCRAPE", 25))
DAYS_TO_SKIP = int(os.getenv("DAYS_TO_SKIP", 7))
TRENDING_DATE_RANGE = os.getenv("TRENDING_DATE_RANGE", "daily").lower()
GITHUB_TRENDING_URL = f"https://github.com/trending?since={TRENDING_DATE_RANGE}"

OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BACKEND_DIR, "output"))
MD_DIR = os.getenv("MD_DIR", os.path.join(OUTPUT_DIR, "md"))
HTML_DIR = os.getenv("HTML_DIR", os.path.join(OUTPUT_DIR, "html"))
DB_PATH = os.getenv("DB_PATH", os.path.join(OUTPUT_DIR, "reporter.db"))

RATE_LIMIT_COPY = int(os.getenv("RATE_LIMIT_COPY", 5))
RATE_LIMIT_EXPORT = int(os.getenv("RATE_LIMIT_EXPORT", 5))

STATS_BASE_CONTRIBUTORS = int(os.getenv("STATS_BASE_CONTRIBUTORS", 10))
STATS_BASE_STARS = int(os.getenv("STATS_BASE_STARS", 100))
STATS_BASE_FORKS = int(os.getenv("STATS_BASE_FORKS", 50))
STATS_MIN_CONTRIBUTORS_SCORE = int(os.getenv("STATS_MIN_CONTRIBUTORS_SCORE", 5))
STATS_MIN_STARS_SCORE = int(os.getenv("STATS_MIN_STARS_SCORE", 10))
STATS_MIN_FORKS_SCORE = int(os.getenv("STATS_MIN_FORKS_SCORE", 5))


def ensure_directories():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)
    os.makedirs(HTML_DIR, exist_ok=True)


ensure_directories()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --border: #dbe4f0;
      --accent: #4f46e5;
      --accent-soft: rgba(79, 70, 229, 0.08);
      --quote: #f8fafc;
      --code: #0f172a;
      --code-bg: #eef2ff;
    }}

    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 32px 20px 56px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      line-height: 1.75;
      color: var(--text);
      background: linear-gradient(180deg, #eef2ff 0%, var(--bg) 220px);
    }}

    .report-shell {{
      max-width: 960px;
      margin: 0 auto;
    }}

    .report-card {{
      overflow: hidden;
      border: 1px solid var(--border);
      border-radius: 24px;
      background: var(--panel);
      box-shadow: 0 24px 80px rgba(15, 23, 42, 0.08);
    }}

    .report-body {{
      padding: 36px 44px 48px;
    }}

    h1, h2, h3, h4, h5, h6 {{
      margin: 1.5em 0 0.65em;
      line-height: 1.35;
      color: var(--text);
    }}

    h1 {{
      margin-top: 0;
      font-size: 32px;
    }}

    h2 {{
      font-size: 24px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--border);
    }}

    h3 {{ font-size: 20px; }}
    h4 {{ font-size: 18px; }}

    p, ul, ol, table, blockquote, pre {{
      margin: 1em 0;
    }}

    ul, ol {{
      padding-left: 1.4em;
    }}

    a {{
      color: var(--accent);
      text-decoration: none;
    }}

    blockquote {{
      margin: 1.25em 0;
      padding: 16px 18px;
      border-left: 4px solid var(--accent);
      border-radius: 0 14px 14px 0;
      background: var(--quote);
    }}

    code {{
      padding: 0.15em 0.45em;
      border-radius: 6px;
      background: var(--code-bg);
      color: var(--code);
      font-family: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
      font-size: 0.9em;
    }}

    pre {{
      overflow-x: auto;
      padding: 18px;
      border-radius: 16px;
      background: #0f172a;
      color: #e2e8f0;
    }}

    pre code {{
      padding: 0;
      background: transparent;
      color: inherit;
    }}

    table {{
      width: 100%;
      overflow: hidden;
      border-collapse: collapse;
      border: 1px solid var(--border);
      border-radius: 14px;
    }}

    th, td {{
      padding: 12px 14px;
      text-align: left;
      vertical-align: top;
      border-bottom: 1px solid var(--border);
    }}

    th {{
      background: #f8fafc;
      font-weight: 600;
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    img {{
      max-width: 100%;
      height: auto;
      border-radius: 14px;
    }}

    hr {{
      margin: 32px 0;
      border: none;
      border-top: 1px solid var(--border);
    }}

    @media (max-width: 768px) {{
      body {{
        padding: 18px 12px 32px;
      }}

      .report-body {{
        padding: 24px 20px 32px;
      }}
    }}
  </style>
</head>
<body>
  <div class="report-shell">
    <article class="report-card">
      <main class="report-body">
        {content}
      </main>
    </article>
  </div>
</body>
</html>
"""
