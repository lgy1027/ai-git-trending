import os
from dotenv import load_dotenv

# 获取 backend 目录路径
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_BASE_URL = os.getenv('LLM_BASE_URL')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4-turbo')
LLM_MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', 3))
LLM_RETRY_DELAY = int(os.getenv('LLM_RETRY_DELAY', 1))
LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', 60))

SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', "09:00")
NUM_PROJECTS_TO_SUMMARIZE = int(os.getenv('NUM_PROJECTS_TO_SUMMARIZE', 8))
MAX_PROJECTS_TO_SCRAPE = int(os.getenv('MAX_PROJECTS_TO_SCRAPE', 25))
DAYS_TO_SKIP = int(os.getenv('DAYS_TO_SKIP', 7))

# 设置输出目录路径 - 指向 backend 目录下的 output 目录
OUTPUT_DIR = os.getenv('OUTPUT_DIR', os.path.join(BACKEND_DIR, 'output'))
MD_DIR = os.getenv('MD_DIR', os.path.join(OUTPUT_DIR, 'md'))
HTML_DIR = os.getenv('HTML_DIR', os.path.join(OUTPUT_DIR, 'html'))
DB_PATH = os.getenv('DB_PATH', os.path.join(OUTPUT_DIR, 'reporter.db'))

# 自动创建必要的目录
def ensure_directories():
    """确保输出目录存在，不存在则自动创建"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)
    os.makedirs(HTML_DIR, exist_ok=True)

# 在模块加载时自动创建目录
ensure_directories()

TRENDING_DATE_RANGE = os.getenv('TRENDING_DATE_RANGE', 'daily').lower()

GITHUB_TRENDING_URL = f"https://github.com/trending?since={TRENDING_DATE_RANGE}"

# IP 限流配置
RATE_LIMIT_COPY = int(os.getenv('RATE_LIMIT_COPY', 5))  # 每个 IP 复制总次数
RATE_LIMIT_EXPORT = int(os.getenv('RATE_LIMIT_EXPORT', 5))  # 每个 IP 导出总次数

# Stats calculation constants
STATS_BASE_CONTRIBUTORS = int(os.getenv('STATS_BASE_CONTRIBUTORS', 10))
STATS_BASE_STARS = int(os.getenv('STATS_BASE_STARS', 100))
STATS_BASE_FORKS = int(os.getenv('STATS_BASE_FORKS', 50))
STATS_MIN_CONTRIBUTORS_SCORE = int(os.getenv('STATS_MIN_CONTRIBUTORS_SCORE', 5))
STATS_MIN_STARS_SCORE = int(os.getenv('STATS_MIN_STARS_SCORE', 10))
STATS_MIN_FORKS_SCORE = int(os.getenv('STATS_MIN_FORKS_SCORE', 5))

SINGLE_PROJECT_PROMPT_TEMPLATE = """
# 角色：顶级技术战略顾问 & 开源项目分析专家

## 任务：基于项目元数据和 README 内容，生成一份全面的、具备战略高度的开源项目分析报告

### 核心原则
1.  **信息融合**: 将元数据（如星标数）与 README 中的信息（如项目目标、架构图）进行交叉验证和深度解读。
2.  **洞察力是关键**: 不要总结，要分析。不要描述，要解读。
3.  **结构化输出**: 严格遵循下方定义的 Markdown 格式，产出专业报告。

### 1. 已知信息 (Input Data)

#### 1.1. GitHub API 元数据
- **项目名称**: `{name}`
- **编程语言**: `{language}`
- **项目描述**: `{description}`
- **项目链接**: `{url}`
- **各项指标**:
    - 星标数: `{stars}` | Forks: `{forks}` | 贡献者: `{contributor_count}`
    - Issue 状态: `{open_issues}` (开放)
    - 创建日期: `{created_at}` | 最近更新: `{updated_at}`

#### 1.2. 项目 README 内容
{readme_content}
````

### 2. 你的分析报告 (Strictly Markdown Output)

  - **风格**: 精准、客观、有深度，同时保持高度可读性。适当使用 Emoji 增强表达力。
  - **指示**: 直接开始输出 Markdown 报告，不要任何前言或结语。

-----

### ✨ {name} ({stars}★) - 深度分析报告

> **一句话总结 (Executive Summary)**: [精准概括项目的核心价值、目标用户和市场定位。]

#### 🚀 价值主张 (Value Proposition)

  - **解决了什么核心问题？**: [根据 README 和描述，清晰地指出项目旨在解决的那个最关键的“痛点”。]
  - **为谁而设计？**: [分析项目的目标用户群体是谁？是前端开发者、数据科学家，还是运维工程师？]
  - **为何与众不同 (Unique Selling Point)？**: [提炼出项目最独特的卖点。是性能、易用性、新范式，还是其他？]

#### 💡 技术架构与实现亮点 (Technical Architecture)

  - **核心架构解读**: [**根据 README 中的信息（可能包含架构图的 ASCII 描述或文字说明）**，解读其核心架构和工作原理。]
  - **关键技术选择**: [分析其在技术选型上的关键决策。例如：为什么选择 Rust？为什么基于某个特定框架？并分析这些选择带来的利弊。]
  - **代码示例解读 (Code Insight)**: [从 README 中挑选一段最能体现其特色的代码示例，并分析其设计之妙。]

#### 📈 社区健康与生态系统 (Community & Ecosystem)

  - **社区健康仪表盘**:
      - **增长势头**: `星标数 {stars}` / `更新频率 {updated_at}` -> [解读这个增长速度和更新频率意味着什么？是爆发期还是稳定期？]
      - **社区互动**: `开放 Issue 数 {open_issues}` / `贡献者数 {contributor_count}` -> [解读社区的健康状况。Issue 多是代表问题多还是讨论活跃？]
  - **生态位分析**:
      - **主要竞品**: [根据项目解决的问题，列出 1-2 个竞品。]
      - **差异化竞争**: [分析 {name} 是如何通过不同的特性、性能或定位来与竞品区分开的。]

#### 🛠️ 上手与应用 (Adoption & Application)

  - **学习曲线评估**: [根据 README 的文档质量和示例丰富度，评估新用户的上手难度（低/中/高）。]
  - **最佳实践场景**: [明确指出最能发挥该项目价值的 2-3 个应用场景。]
  - **潜在风险与避坑指南**: [指出在实际应用中可能遇到的坑，或需要注意的配置、依赖问题。]

#### 🔗 项目链接

  - **GitHub**: [{name}](https://www.google.com/search?q=%7Burl%7D)

"""

SINGLE_PROJECT_PROMPT_TEMPLATE_CACHE = """
# 角色：资深技术分析师与博主

## 任务：对以下这个 GitHub 项目进行一次深刻且生动的单点分析

### 项目信息
- **项目名称**: `{name}`
- **编程语言**: `{language}`
- **项目描述**: `{description}`
- **项目链接**: `{url}`
- **总星标数**: `{stars}`
- **Forks**: `{forks}`
- **贡献者数量**: `{contributor_count}`
- **创建日期**: `{created_at}`
- **最近更新**: `{updated_at}`
- **开放Issue数**: `{open_issues}`
- **Watchers**: `{watchers}`

### 写作要求
- **风格**: 专业、风趣、有洞见，多使用 Emoji ✨💡🚀📈🤔 增加可读性。
- **结构**: 必须包含以下几个部分，并使用 Markdown 加以组织：
    - `### ✨ {name} ({stars}星)）`
    - `**一句话点评**: [用一句话精彩地概括其核心价值]`
    - `**💡 技术亮点与创新**: [深入分析其技术栈、实现方式或设计思路的过人之处]`
    - `**📈 潜在影响与应用**: [探讨它可能对行业带来的改变，或在哪些具体场景下能大放异彩]`
    - `**🔗 项目链接**: [{name}]({url})`
- **纯净度**: **直接输出该项目的 Markdown 分析内容，不要任何额外的解释或客套话。**
"""

OVERVIEW_PROMPT_TEMPLATE = """
# 角色：顶尖技术分析师

## 任务：根据今日的热点项目列表，生成一段简明扼要的摘要。

### 今日焦点项目列表
{project_details}

### 要求
- **风格**: 专业、精炼、信息导向。
- **内容**:
    1.  **主题概括**: 用一句话点出今天上榜项目的主要技术领域或趋势（例如：AI Infra、开发工具、多模态应用等）。
    2.  **范围说明**: 概括项目范围，提及一些具体的例子，格式为“从...到...”。
    3.  **结尾**: 固定以“具体项目摘要如下：”结尾，确保与后续内容无缝衔接。
- **格式**: 输出一个简洁的段落，使用 Markdown `##` 作为主标题。
- **示例**:
    `## 今日热点：AI Infra 与多模态应用持续升温`
    `今天的 GitHub 热榜涵盖了从底层的 AI 基础设施到上层的多模态应用等多个领域。具体项目摘要如下：`
- **纯净度**: **只输出摘要部分，不要任何其他无关文字。**
"""

ENTITY_PROMPT_TEMPLATE = """
# 角色：顶尖技术战略分析师

## 任务：基于以下开发者/组织信息，生成一段精辟的“速览”点评。

### 实体信息
- **名称**: `{name}` ({type})
- **简介**: {bio}
- **创建于**: {created_at}
- **关注者**: {followers}
- **公开仓库数**: {public_repos}

### 旗下知名仓库
{top_repos}

### 技术栈偏好分析
- **主要语言**: {main_languages}

### 写作要求
- **风格**: 专业、有洞察力、数据驱动。
- **结构**:
    - `**技术影响力**: [一句话总结其在技术社区的地位和影响力]`
    - `**技术栈偏好**: [分析其主要使用的编程语言和技术领域]`
    - `**核心领域**: [判断其专注的核心方向，例如：AI Infra、前端工具、数据科学等]`
- **纯净度**: **直接输出 Markdown 格式的点评，不要任何额外解释。**
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Noto Sans SC', sans-serif;
            line-height: 1.8;
            color: #34495e;
            background: linear-gradient(to right bottom, #fdfbfb, #ebedee);
            margin: 0;
            padding: 20px;
        }}
        .main-container {{
            max-width: 850px;
            margin: 40px auto;
            background-color: #ffffff;
            padding: 30px 50px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
            font-weight: 700;
        }}
        h1 {{
            font-size: 2.2em;
            text-align: center;
            margin-bottom: 20px;
            border-bottom: none;
        }}
        h2 {{
            font-size: 1.6em;
            margin-top: 50px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        .card {{
            background: #f9f9f9;
            border-left: 5px solid #3498db;
            padding: 20px;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        code {{
            background-color: #e8f6ff;
            color: #2980b9;
            padding: 3px 6px;
            border-radius: 4px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #2c3e50;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}
        a {{
            color: #2980b9;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s ease;
        }}
        a:hover {{
            color: #1f618d;
            text-decoration: underline;
        }}
        ul, ol {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 12px;
        }}
        .footer {{
            text-align: center;
            margin-top: 60px;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        {content}
        <div class="footer">
            <p>❤️ Generated by GitHub Trending Reporter</p>
        </div>
    </div>
</body>
</html>
"""
