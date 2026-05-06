# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**AI Git Trending** 是一个自动化分析 GitHub Trending 的机器人，为您每日精选、总结并生成技术洞察报告。

## 主要功能

1. **每日追踪与分析** - 自动抓取 GitHub Trending 热门项目，利用 LLM 进行深度分析
2. **AI 驱动的项目分析** - 生成"一句话点评"、"技术亮点"、"项目定位"等洞察
3. **交互式 Web 界面** - Vue.js 前端，支持报告浏览、搜索、筛选
4. **趋势分析看板** - 多维度数据分析（热门语言分布、星标蹿升、技术领域分析）
5. **数据持久化** - SQLite 存储历史数据，支持趋势分析

## 技术栈

- **后端**: Python 3.x, Flask, SQLite
- **前端**: Vue.js 3, TypeScript, Vite, Pinia, Vue Router, TailwindCSS
- **AI 集成**: OpenAI SDK (支持多种 LLM 服务)
- **部署**: Docker / Docker Compose

## 常用命令

### 后端

```bash
cd backend

# 运行完整服务（Web API + 定时任务）- 推荐
python app.py

# 仅运行 Web API 服务（前端开发时使用）
python app.py --mode web --debug

# 仅运行定时报告生成器
python app.py --mode reporter

# 自定义端口和地址
python app.py --host 0.0.0.0 --port 5001 --debug
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 类型检查
npm run type-check

# 代码检查与修复
npm run lint

# 构建生产版本
npm run build
```

### Docker

```bash
docker compose up
```

## 环境配置

### 后端配置 (backend/.env)

```env
LLM_API_KEY="your_api_key"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4-turbo"
SCHEDULE_TIME="09:00"
NUM_PROJECTS_TO_SUMMARIZE=8
MAX_PROJECTS_TO_SCRAPE=25
TRENDING_DATE_RANGE=daily
```

### 前端配置 (frontend/.env)

```env
VITE_API_BASE_URL=http://localhost:5001
```

## 项目结构

```
├── backend/               # Flask 后端
│   ├── app.py            # 主入口，支持三种运行模式
│   ├── router.py         # Flask API 路由定义
│   ├── config/           # 配置模块
│   │   ├── settings.py   # 环境变量配置
│   │   └── logging_config.py
│   └── app/
│       ├── main.py       # 定时任务入口
│       ├── scraper.py    # GitHub 数据抓取
│       ├── summarizer.py # LLM 分析生成
│       ├── analyzer.py   # 趋势数据分析
│       ├── database.py   # SQLite 数据库操作
│       ├── github_api.py # GitHub API 调用
│       └── file_writer.py# 报告文件输出

├── frontend/             # Vue.js 前端
│   ├── src/
│   │   ├── views/       # 页面视图 (Home, Reports, Rankings, TrendAnalysis 等)
│   │   ├── components/  # 可复用组件
│   │   ├── api/         # API 调用封装
│   │   └── composables/ # Vue 组合式函数
│   └── package.json
```

## 架构概要

### 后端架构

后端采用 **Flask 蓝图模块化设计**，主要分为：

- **路由层** (`router.py`) - 直接定义 Flask 路由，处理 HTTP 请求
- **路由模块** (`routes/`) - 使用蓝图注册的项目(`projects_bp`)和统计(`stats_bp`)
- **业务层** (`app/`) - 核心业务逻辑
- **配置层** (`config/`) - 环境变量和日志配置

### 数据模型（星型模型）

数据库采用星型模型设计，支持历史趋势分析：

- **维度表**: `dim_projects`, `dim_languages`, `dim_tags`, `dim_dates`
- **事实表**: `fact_trending_snapshots` - 记录每日趋势快照
- **汇总表**: `summarized_projects` - AI 分析后的项目汇总

### 前端架构

Vue 3 + TypeScript 单页应用：

- **视图** (`views/`) - Home, Reports, Rankings, TrendAnalysis 等页面
- **组件** (`components/`) - ProjectCard, ProjectModal, StatsChart 等
- **状态管理** - Pinia store
- **API 调用** - axios 封装

### 定时任务流程

```
job() → scrape_github_trending() → add_trending_snapshots()
     → 筛选新项目 → get_summary_for_single_project(LLM)
     → save_summary_files() → 生成 Markdown/HTML 报告
```

## API 端点

| 端点 | 描述 |
|------|------|
| `/api/reports` | 获取所有报告列表 |
| `/api/report/<date_str>` | 获取指定日期报告内容 |
| `/api/trends` | 获取趋势数据 (支持 days 参数: 7/30/182/365) |
| `/api/stats` | 获取统计信息 |
| `/api/language-distribution` | 获取语言分布 |
| `/api/project/<name>` | 获取项目详情 |
| `/api/trend-data` | 获取趋势指标数据 |
| `/api/download/<date_str>/<format>` | 下载报告 (md/html)，带 IP 限流 |
| `/api/copy/<date_str>` | 复制报告内容，带 IP 限流 |
| `/api/rate-limit-status` | 获取当前 IP 限流状态 |

## 关键模块

- **summarizer.py** - LLM 调用核心，支持自定义 Prompt 生成项目分析、技术领域分类
- **analyzer.py** - 趋势数据分析，计算项目排名、语言分布等
- **database.py** - SQLite 封装，支持事实表/维度表设计
- **scraper.py** - GitHub Trending 页面抓取
- **cache.py** - IP 限流实现


# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.