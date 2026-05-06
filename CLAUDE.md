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
- **前端**: Vue.js 3, TypeScript, Vite, TailwindCSS
- **AI 集成**: OpenAI SDK (支持多种 LLM 服务)
- **部署**: Docker / Docker Compose

## 常用命令

### 后端

```bash
cd backend

# 运行完整服务（Web API + 定时任务）
python app.py

# 仅运行 Web API 服务（前端开发时使用）
python app.py --mode web --debug

# 仅运行定时报告生成器
python app.py --mode reporter

# 自定义端口
python app.py --host 0.0.0.0 --port 5001 --debug
```

### 前端

```bash
cd frontend
npm install
npm run dev
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

## API 端点

| 端点 | 描述 |
|------|------|
| `/api/reports` | 获取所有报告列表 |
| `/api/report/<date_str>` | 获取指定日期报告内容 |
| `/api/trends` | 获取趋势数据 |
| `/api/stats` | 获取统计信息 |
| `/api/language-distribution` | 获取语言分布 |
| `/api/project/<name>` | 获取项目详情 |
| `/api/trend-data` | 获取趋势指标数据 |

## 关键模块

- **summarizer.py** - LLM 调用核心，支持自定义 Prompt 生成项目分析、技术领域分类
- **analyzer.py** - 趋势数据分析，计算项目排名、语言分布等
- **database.py** - SQLite 封装，支持事实表/维度表设计
