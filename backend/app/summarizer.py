from collections import Counter
import re
import time

from openai import OpenAI

from config.logging_config import get_logger
from config.settings import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MAX_RETRIES,
    LLM_MODEL,
    LLM_RETRY_DELAY,
    LLM_TIMEOUT,
)
from .github_api import get_entity_details, get_entity_repos

logger = get_logger("summarizer", "INFO")

TECH_DOMAINS = [
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

DOMAIN_KEYWORDS = {
    "AI/ML": ["人工智能", "AI", "机器学习", "ML", "深度学习", "神经网络", "模型训练", "算法"],
    "LLM Apps": ["LLM", "大模型", "ChatGPT", "Claude", "AIGC", "生成式 AI", "RAG", "智能体", "Agent"],
    "Web": ["Web", "后端", "API", "REST", "GraphQL", "HTTP", "服务端"],
    "Frontend": ["前端", "React", "Vue", "Angular", "Svelte", "UI", "CSS", "JavaScript", "TypeScript"],
    "Mobile": ["移动", "iOS", "Android", "Flutter", "React Native", "Swift", "Kotlin", "小程序"],
    "DevOps": ["DevOps", "Docker", "Kubernetes", "K8S", "CI/CD", "容器", "部署", "Terraform"],
    "Data Science": ["数据科学", "数据分析", "Pandas", "NumPy", "Jupyter", "统计", "可视化"],
    "Database": ["数据库", "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "ORM"],
    "Tools": ["工具", "CLI", "命令行", "SDK", "开发工具", "自动化", "效率"],
    "Security": ["安全", "加密", "Auth", "OAuth", "JWT", "权限", "隐私", "漏洞"],
    "Blockchain": ["区块链", "Blockchain", "Web3", "以太坊", "Solidity", "智能合约", "Crypto", "DeFi"],
    "Gaming": ["游戏", "Game", "Unity", "Unreal", "3D", "VR", "AR", "引擎"],
    "OS": ["操作系统", "Kernel", "系统编程", "Rust", "C/C++", "驱动", "底层"],
    "IoT": ["物联网", "IoT", "传感器", "嵌入式", "Arduino", "树莓派", "MCU"],
}

OVERVIEW_HEADING_PATTERN = re.compile(r"(?m)^##\s+.+$")
PROJECT_HEADING_PATTERN = re.compile(r"(?m)^#\s+.+$")
ENTITY_LINE_PATTERNS = (
    re.compile(r"(?m)^\*\*技术影响力\*\*[:：]\s*.+$"),
    re.compile(r"(?m)^\*\*技术栈偏好\*\*[:：]\s*.+$"),
    re.compile(r"(?m)^\*\*核心领域\*\*[:：]\s*.+$"),
)

OVERVIEW_SYSTEM_PROMPT = """你是资深技术编辑。
你只输出最终答案，不输出思考过程、草稿、解释、提示词复述、样例、标签或代码块。
输出语言必须是简体中文。"""

PROJECT_SYSTEM_PROMPT = """你是资深开源项目分析师。
你只输出最终 Markdown，不输出思考过程、草稿、解释、提示词复述、样例、XML 标签、<think> 标签或代码块围栏。
输出语言必须是简体中文，内容要具体、克制、有判断。"""

ENTITY_SYSTEM_PROMPT = """你是资深技术生态分析师。
你只输出最终 Markdown，不输出思考过程、草稿、解释、提示词复述、样例、标签或代码块。
输出语言必须是简体中文。"""

MAX_README_CHARS = 12000
LLM_MAX_TOKENS = 2400

_llm_client = None


def normalize_tech_domain(domain_text: str) -> str:
    if not domain_text:
        return "Other"

    domain_text = domain_text.strip().lower()

    for domain in TECH_DOMAINS:
        if domain_text == domain.lower():
            return domain

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in domain_text:
                return domain

    return "Other"


def extract_tech_domain(content: str) -> str:
    if not content:
        return "Other"

    patterns = (
        re.compile(r"(?m)^\*\*核心领域\*\*[:：]\s*(.+)$"),
        re.compile(r"(?m)^-\s+\*\*核心领域\*\*[:：]\s*(.+)$"),
    )
    for pattern in patterns:
        match = pattern.search(content)
        if match:
            return normalize_tech_domain(match.group(1).strip())

    return "Other"


def validate_llm_config():
    if not LLM_API_KEY:
        return False, "LLM_API_KEY is not configured"
    if not LLM_BASE_URL:
        return False, "LLM_BASE_URL is not configured"
    if not LLM_BASE_URL.rstrip("/").endswith("/v1"):
        return False, "LLM_BASE_URL must include the /v1 suffix"
    return True, None


def get_llm_client():
    global _llm_client

    if _llm_client is None:
        is_valid, error = validate_llm_config()
        if not is_valid:
            logger.warning(f"LLM client not initialized: {error}")
            return None
        try:
            _llm_client = OpenAI(
                api_key=LLM_API_KEY,
                base_url=LLM_BASE_URL.rstrip("/"),
                timeout=LLM_TIMEOUT,
            )
            logger.info(f"LLM client initialized successfully (timeout={LLM_TIMEOUT}s)")
        except Exception as exc:
            logger.error(f"Failed to initialize LLM client: {exc}")
            return None

    return _llm_client


def extract_message_content(message) -> str:
    if message is None:
        return ""

    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and item.get("text"):
                    text_parts.append(item["text"])
            else:
                item_type = getattr(item, "type", None)
                item_text = getattr(item, "text", None)
                if item_type == "text" and item_text:
                    text_parts.append(item_text)
        return "\n".join(part.strip() for part in text_parts if part).strip()

    return ""


def strip_meta_lines(content):
    if not content:
        return content

    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", content)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)

    meta_patterns = [
        r"(?im)^.*?\bpotential output\b.*$",
        r"(?im)^.*?\blet'?s craft final answer\b.*$",
        r"(?im)^.*?\bwait need to ensure\b.*$",
        r"(?im)^.*?\bwe'?ll produce\b.*$",
        r"(?im)^.*?\bcheck that we used\b.*$",
        r"(?im)^.*?\bwrite one sentence\b.*$",
        r"(?im)^.*?\bensure formatting\b.*$",
        r"(?im)^.*?\boutput must\b.*$",
        r"(?im)^.*?\bso just output\b.*$",
        r"(?im)^.*?\bjust the commentary\b.*$",
        r"(?im)^.*?\bhere'?s\b.*$",
        r"(?im)^.*?\banalysis[:：]?\s*$",
        r"(?im)^.*?\bfinal answer[:：]?\s*$",
    ]
    for pattern in meta_patterns:
        cleaned = re.sub(pattern, "", cleaned)

    lines = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if stripped.startswith("`") and stripped.endswith("`"):
            continue
        lines.append(line.rstrip())

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def build_overview_prompt(projects):
    project_details = "\n".join(
        [f"- {project['name']}: {project.get('description', 'No description')}" for project in projects]
    )
    return f"""请基于下面的 GitHub 热门项目列表，写一段面向开发者的“今日热点”总览。

项目列表：
{project_details}

输出要求：
1. 严格只输出两行，不要多写。
2. 第一行必须是 Markdown 二级标题，格式：## 今日热点：<一句话主题判断>
3. 第二行必须是一整段中文，不要分点，不要换行。
4. 这段话要回答三个问题：今天真正的技术主线是什么、这些项目为什么值得开发者关注、它们大致覆盖了哪些方向。
5. 语气要像技术情报编辑的判断，不要写成宣传稿，也不要只是项目名罗列。
6. 最后一句固定以“具体项目摘要如下：”结尾。
7. 不要输出任何思考过程、提示词复述、样例、解释或标签。
"""


def build_overview_retry_prompt(projects):
    project_details = "\n".join(
        [f"- {project['name']}: {project.get('description', 'No description')}" for project in projects]
    )
    return f"""请根据下面的热门项目，输出开发者视角的今日热点总览：

{project_details}

严格只输出两行：
第一行：## 今日热点：<一句话主题>
第二行：一句中文判断，说明今天最值得关注的技术趋势，并以“具体项目摘要如下：”结尾。
不要输出解释、草稿或思考过程。
"""


def build_project_prompt(project):
    readme_content = (project.get("readme_content") or "README content not available.")[:MAX_README_CHARS]
    return f"""请基于下面的项目信息，生成一份更像“开发者情报”的 GitHub 热点项目分析。

项目元数据：
- 名称：{project['name']}
- 链接：{project.get('url', '')}
- 描述：{project.get('description', 'N/A')}
- 语言：{project.get('language', 'N/A')}
- Stars：{project.get('stars', 0)}
- Forks：{project.get('forks', 0)}
- Contributor Count：{project.get('contributor_count', 0)}
- Open Issues：{project.get('open_issues', 0)}
- Watchers：{project.get('watchers', 0)}
- Created At：{project.get('created_at', 'N/A')}
- Updated At：{project.get('updated_at', 'N/A')}

README 素材：
{readme_content}

请严格输出以下 Markdown 结构，不要多写：
# {project['name']} - 深度分析报告
> **一句话总结**：用一句中文说清它是什么、适合谁、为什么值得看

## 热点判断
- **为什么火**：判断它近期走红的核心原因，是技术突破、产品体验、模型风口、传播效应还是生态位置
- **值得关注吗**：一句判断它对开发者的实际价值，避免空话

## 问题与价值
- **解决问题**：它替代了什么旧做法，或者明显改善了哪段工作流
- **目标用户**：最适合哪类开发者、团队或场景
- **核心价值**：一句话说明它最打动人的点

## 技术拆解
- **关键机制**：点出架构、交互方式或实现路径里最值得看的部分
- **技术取舍**：分析它为了速度、体验、成本、集成度做了什么取舍
- **核心领域**：只能输出一个固定分类，必须从以下选一个：AI/ML、LLM Apps、Web、Frontend、Mobile、DevOps、Data Science、Database、Tools、Security、Blockchain、Gaming、OS、IoT、Other

## 落地评估
- **上手门槛**：判断开发者试用它的难度，结合文档、依赖、部署方式来写
- **生产可用性**：判断它更像 demo、实验品、团队工具，还是可以进入真实流程

## 风险提示
- **主要风险**：指出维护、生态、模型依赖、许可、性能或安全中的关键风险
- **需要继续观察**：说出一个后续最值得跟踪的信号

## 结论
- **建议动作**：只能从“值得立刻试用 / 值得持续跟踪 / 可以先观望”中选一个
- **判断依据**：用一句话解释为什么给这个建议

## 项目链接
- **GitHub**：{project.get('url', '')}

写作要求：
1. 全部使用简体中文。
2. 语气像技术分析师，不像宣传稿。
3. 每个要点都要具体，优先写判断和取舍，不要重复 README 原文。
4. 不要输出思考过程、提示词、样例、前言、后记或代码块围栏。
"""


def build_project_retry_prompt(project):
    readme_content = (project.get("readme_content") or "README content not available.")[:6000]
    return f"""请基于下面信息，输出一份简洁但有判断的开发者情报。

项目：{project['name']}
描述：{project.get('description', 'N/A')}
语言：{project.get('language', 'N/A')}
Stars：{project.get('stars', 0)}
Forks：{project.get('forks', 0)}
链接：{project.get('url', '')}
README 摘要：
{readme_content}

严格输出以下 Markdown：
# {project['name']} - 深度分析报告
> **一句话总结**：一句话说清它是什么、为什么值得看

## 热点判断
- **为什么火**：一句话判断热度来源
- **值得关注吗**：一句话判断开发者是否该关注

## 技术拆解
- **关键机制**：一句话写出最值得看的实现点
- **核心领域**：只能从 AI/ML、LLM Apps、Web、Frontend、Mobile、DevOps、Data Science、Database、Tools、Security、Blockchain、Gaming、OS、IoT、Other 中选一个

## 落地评估
- **适用场景**：一句话说明适合谁
- **主要风险**：一句话说明最大风险

## 结论
- **建议动作**：只能从“值得立刻试用 / 值得持续跟踪 / 可以先观望”中选一个
- **判断依据**：一句话解释原因

## 项目链接
- **GitHub**：{project.get('url', '')}

不要输出思考过程、解释或多余前后文。
"""


def build_entity_prompt(owner, entity_details, top_repos, main_languages):
    top_repos_str = "\n".join(
        [f"- {repo['name']} ({repo['stars']} stars, {repo['language']})" for repo in top_repos]
    ) or "- 暂无代表仓库"
    return f"""请基于下面的 GitHub 开发者 / 组织信息，输出一个极简但有判断的技术画像。

实体信息：
- 名称：{entity_details.get('name', owner)}
- 类型：{entity_details.get('type', 'N/A')}
- 简介：{entity_details.get('bio', 'N/A')}
- 创建时间：{entity_details.get('created_at', 'N/A')}
- Followers：{entity_details.get('followers', 0)}
- Public Repos：{entity_details.get('public_repos', 0)}

代表仓库：
{top_repos_str}

主要语言：
{main_languages}

只输出下面三行 Markdown，不要多写：
**技术影响力**：一句话概括其在技术社区里的位置，说明是头部组织、垂直专家、新兴作者还是热门项目驱动型账号
**技术栈偏好**：一句话总结其主要技术方向和语言偏好，不要只机械罗列
**核心领域**：一句话判断其主要聚焦领域，并尽量与其代表项目保持一致
"""


def call_llm_with_retry(prompt, model, temperature, max_retries=None, delay=None, system_prompt=None):
    if max_retries is None:
        max_retries = LLM_MAX_RETRIES
    if delay is None:
        delay = LLM_RETRY_DELAY

    client = get_llm_client()
    if client is None:
        logger.error("LLM client not available")
        return None

    last_exception = None
    for attempt in range(max_retries):
        try:
            logger.debug(f"LLM API call attempt {attempt + 1}/{max_retries}")
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=LLM_MAX_TOKENS,
            )
            choice = response.choices[0] if response.choices else None
            message = choice.message if choice else None
            raw_content = extract_message_content(message)
            if not raw_content:
                reasoning = getattr(message, "reasoning", None) or ""
                reasoning = reasoning.strip() if isinstance(reasoning, str) else ""
                if reasoning:
                    logger.warning("LLM returned reasoning but no final content")
            clean_content = strip_meta_lines(raw_content)
            logger.debug(f"LLM API call succeeded on attempt {attempt + 1}")
            return clean_content
        except Exception as exc:
            last_exception = exc
            error_msg = str(exc)
            if "timeout" in error_msg.lower() or "504" in error_msg or "Gateway" in error_msg:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} timed out")
            else:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {exc}")

            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    logger.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
    return None


def extract_overview_intro(content):
    if not content:
        return None

    normalized = strip_meta_lines(content.strip())
    match = OVERVIEW_HEADING_PATTERN.search(normalized)
    if not match:
        return normalized

    remainder = normalized[match.start():].strip()
    lines = remainder.splitlines()
    kept_lines = []
    body_started = False

    for line in lines:
        stripped = line.strip()

        if not kept_lines:
            kept_lines.append(line.rstrip())
            continue

        if not stripped:
            if body_started:
                break
            continue

        if line.startswith("#"):
            break

        kept_lines.append(line.rstrip())
        body_started = True

    cleaned = "\n".join(kept_lines).strip()
    return cleaned or normalized


def extract_project_report(content):
    if not content:
        return None

    normalized = strip_meta_lines(content.strip())
    match = PROJECT_HEADING_PATTERN.search(normalized)
    if not match:
        return normalized

    return normalized[match.start():].strip()


def extract_entity_summary(content):
    if not content:
        return None

    normalized = strip_meta_lines(content.strip())
    lines = []
    for pattern in ENTITY_LINE_PATTERNS:
        match = pattern.search(normalized)
        if match:
            lines.append(match.group(0).strip())

    if lines:
        return "\n".join(lines)

    fallback_lines = []
    for line in normalized.splitlines():
        stripped = line.strip()
        if stripped.startswith("**技术影响力**") or stripped.startswith("**技术栈偏好**") or stripped.startswith("**核心领域**"):
            fallback_lines.append(stripped)

    return "\n".join(fallback_lines).strip() or normalized


def get_entity_summary(owner):
    logger.info(f"Fetching details for entity: {owner}")
    entity_details = get_entity_details(owner)
    if not entity_details:
        return ""

    top_repos = get_entity_repos(owner)
    languages = [repo["language"] for repo in top_repos if repo["language"] and repo["language"] != "N/A"]
    main_languages = ", ".join(
        dict.fromkeys(lang for lang, _count in Counter(languages).most_common(3))
    ) if languages else "多样化或未指定"

    prompt = build_entity_prompt(owner, entity_details, top_repos, main_languages)
    summary = call_llm_with_retry(prompt, LLM_MODEL, 0.2, system_prompt=ENTITY_SYSTEM_PROMPT)
    if summary:
        summary = extract_entity_summary(summary)
        return f"\n\n#### 开发者 / 组织速览\n\n{summary}"

    logger.error(f"Error generating entity summary for {owner}")
    return ""


def get_summary_for_single_project(project):
    logger.info(f"Analyzing project: {project['name']}...")
    if "readme_content" not in project:
        project["readme_content"] = "README content not available."

    prompt = build_project_prompt(project)
    project_summary = call_llm_with_retry(prompt, LLM_MODEL, 0.3, system_prompt=PROJECT_SYSTEM_PROMPT)
    if not project_summary:
        logger.warning(f"Primary project prompt failed for {project['name']}, retrying with simplified prompt.")
        retry_prompt = build_project_retry_prompt(project)
        project_summary = call_llm_with_retry(retry_prompt, LLM_MODEL, 0.2, system_prompt=PROJECT_SYSTEM_PROMPT)
        if not project_summary:
            logger.error(f"Error calling LLM API for {project['name']}: Failed after retries.")
            return None

    project_summary = extract_project_report(project_summary)

    try:
        owner = project["name"].split("/")[0]
        entity_summary = get_entity_summary(owner)
    except (IndexError, AttributeError):
        entity_summary = ""

    return project_summary + entity_summary


def get_overview_intro(projects):
    logger.info("Generating overview introduction...")
    prompt = build_overview_prompt(projects)

    overview = call_llm_with_retry(prompt, LLM_MODEL, 0.2, system_prompt=OVERVIEW_SYSTEM_PROMPT)
    if overview:
        return extract_overview_intro(overview)

    logger.warning("Primary overview prompt failed, retrying with simplified prompt.")
    retry_prompt = build_overview_retry_prompt(projects)
    overview = call_llm_with_retry(retry_prompt, LLM_MODEL, 0.1, system_prompt=OVERVIEW_SYSTEM_PROMPT)
    if overview:
        return extract_overview_intro(overview)

    logger.error("Error calling LLM API for overview: Failed after retries.")
    return "## 今日热点：GitHub 热门趋势\n今天的热门项目覆盖了多个技术方向，具体项目摘要如下："
