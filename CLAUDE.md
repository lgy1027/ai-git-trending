# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**AI Git Trending** 是一个自动化分析 GitHub Trending 的机器人，为您每日精选、总结并生成技术洞察报告。

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

# 开发模式（自动代理 API 到后端）
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
GITHUB_API_TOKEN="optional_github_token"
```

### 前端配置 (frontend/.env)

```env
VITE_API_BASE_URL=http://localhost:5001
```

## 架构概要

### 后端架构

```
backend/
├── app.py              # 主入口，支持 --mode full/web/reporter
├── router.py           # 直接定义的 Flask 路由
├── config/             # 配置模块
│   ├── settings.py     # 环境变量配置（核心配置）
│   └── logging_config.py
├── app/                # 核心业务逻辑
│   ├── main.py         # 定时任务入口
│   ├── scraper.py      # GitHub Trending 页面抓取（BeautifulSoup）
│   ├── summarizer.py   # LLM 调用核心，生成项目分析
│   ├── analyzer.py     # 趋势数据分析，计算排名、语言分布
│   ├── database.py     # SQLite 数据库操作
│   ├── github_api.py   # GitHub API 调用
│   ├── file_writer.py  # 报告文件输出
│   └── cache.py        # IP 限流实现
└── routes/             # 蓝图路由模块
    ├── projects.py     # 项目相关 API (projects_bp)
    ├── stats.py        # 统计相关 API (stats_bp)
    └── common.py       # 通用 API
```

### 数据模型（星型模型）

数据库采用星型模型设计，支持历史趋势分析：

- **维度表**: `dim_projects`, `dim_languages`, `dim_tags`, `dim_dates`
- **事实表**: `fact_trending_snapshots` - 记录每日趋势快照
- **汇总表**: `summarized_projects` - AI 分析后的项目汇总

### 前端架构

```
frontend/src/
├── views/              # 页面视图
│   ├── Home.vue        # 首页（报告浏览）
│   ├── Reports.vue     # 报告列表
│   ├── Rankings.vue    # 排行榜
│   └── TrendAnalysis.vue  # 趋势分析
├── components/         # 可复用组件
│   ├── ProjectCard.vue # 项目卡片
│   ├── ProjectModal.vue # 项目详情弹窗
│   └── StatsChart.vue  # 统计图表
├── api/                # API 调用封装 (axios)
├── composables/        # Vue 组合式函数
├── stores/             # Pinia 状态管理
└── router/             # Vue Router 配置
```

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
| `/api/projects/<date>` | 获取指定日期项目列表 |
| `/api/project/<name>` | 获取项目详情 |
| `/api/trends` | 获取趋势数据 (支持 days 参数: 7/30/182/365) |
| `/api/stats` | 获取统计信息 |
| `/api/language-distribution` | 获取语言分布 |
| `/api/trend-data` | 获取趋势指标数据 |
| `/api/download/<date_str>/<format>` | 下载报告 (md/html)，带 IP 限流 |
| `/api/copy/<date_str>` | 复制报告内容，带 IP 限流 |
| `/api/rate-limit-status` | 获取当前 IP 限流状态 |

## 关键模块说明

- **summarizer.py** - LLM 调用核心，支持自定义 Prompt 生成项目分析、技术领域分类
- **analyzer.py** - 趋势数据分析，计算项目排名、语言分布、技术领域统计
- **database.py** - SQLite 封装，星型模型设计，支持事实表/维度表查询
- **scraper.py** - GitHub Trending 页面抓取，使用 BeautifulSoup 解析
- **cache.py** - IP 限流实现，基于内存的简单限流机制
- **router.py** - 直接定义的 Flask 路由（非蓝图）
- **routes/** - 蓝图注册的项目和统计路由

---

## 开发指南

**避免过度设计**：
- 不做过度抽象，单用途代码不需要抽象成通用模块
- 不添加未请求的可配置项
- 不处理不可能出现的异常场景

**精确修改**：
- 只修改与任务直接相关的代码
- 不改善相邻代码的格式或注释
- 匹配现有代码风格

**目标驱动**：
- 将任务转化为可验证的目标
- 多步骤任务先列出计划再执行
