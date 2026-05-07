# GitHub Trending Reporter 🚀

[English](./README-EN.md) | 简体中文

**一个自动化分析 GitHub Trending 的机器人，为您每日精选、总结并生成技术洞察报告。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Backend-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Framework](https://img.shields.io/badge/Frontend-Vue.js-blue.svg)](https://vuejs.org/)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)

---

## ✨ 项目亮点

- **📈 每日追踪与分析**: 自动抓取 GitHub Trending 的最新热门项目，并利用大语言模型（LLM）进行深度分析，产出"一句话点评"、"技术亮点"和"潜在影响"等洞察。
- **🌐 交互式 Web 界面**: 基于 Vue.js 构建的现代化前端，提供美观的报告浏览、搜索和筛选功能，支持响应式设计。
- **🚀 多维度数据分析**: 内置趋势分析看板，可查看"上榜最频繁项目"、"热门语言分布"、"星标蹿升最快项目"和"技术领域分析"，助您全面洞察技术潮流。
- **⚙️ 灵活高度可配**: 从 LLM 模型、API 地址到抓取频率、报告数量，几乎所有核心参数均可通过环境变量轻松配置。
- **📦 开箱即用**: 提供 Docker 支持，一键启动，无需繁琐的环境配置；同时支持多种运行模式（完整服务、仅Web、仅报告生成器）。
- **💾 数据持久化**: 使用 SQLite 数据库存储历史数据，避免重复分析，并支持趋势分析功能。

## 📊 输出示例

项目会在 `output` 目录生成每日报告。

### Markdown 报告 (`.md`)

结构清晰的 Markdown 文件，可直接发布到各类平台。

```markdown
## 🚀 AI 浪潮继续席卷，今天 GitHub 上有几款颠覆性的开源模型！

### ✨ awesome-project

**一句话点评**: 解决 X 领域痛点的革命性工具。
**💡 技术亮点与创新**: 采用最新的 A 技术和 B 框架，特别巧妙的 C 设计模式。
**📈 潜在影响与应用**: 有望在 Y 行业树立新标准，特别适合 X、Y、Z 场景。
**🔗 项目链接**: [awesome-project](https://github.com/user/awesome-project)

---

### ✨ another-cool-repo

**一句话点评**: ...
...
```

![Markdown 示例](images/image.png)

### 交互式 Web 界面

现代化卡片式设计的 HTML 文件，提供更好的视觉阅读体验。

![Web 界面示例](images/web.png)

## 🛠️ 技术栈

- **后端**: Python 3.x, Flask
- **前端**: Vue.js 3, TypeScript, Vite, Pinia, TailwindCSS
- **数据抓取**: `requests`, `BeautifulSoup4`
- **AI 集成**: `openai`
- **任务调度**: `schedule`
- **数据库**: `SQLite`
- **部署**: `Docker`

## 📁 项目结构

项目采用前后端分离的架构设计：

```
├── backend/           # 后端代码目录
│   ├── app.py         # 主程序入口（支持三种运行模式）
│   ├── router.py      # API 路由定义
│   ├── config/        # 配置模块
│   │   ├── settings.py      # 环境变量配置
│   │   └── logging_config.py
│   ├── app/           # 核心功能模块
│   │   ├── analyzer.py      # 数据分析功能
│   │   ├── summarizer.py    # AI 总结生成
│   │   ├── scraper.py       # GitHub 数据抓取
│   │   ├── database.py      # 数据库操作
│   │   ├── github_api.py    # GitHub API 调用
│   │   ├── file_writer.py   # 报告文件输出
│   │   ├── cache.py         # IP 限流实现
│   │   └── main.py          # 任务执行入口
│   └── routes/        # 蓝图路由模块
│       ├── projects.py      # 项目相关 API
│       ├── stats.py         # 统计相关 API
│       └── common.py        # 通用 API
├── frontend/          # 前端代码目录
│   ├── src/           # Vue.js 源码
│   │   ├── views/           # 页面视图
│   │   ├── components/      # 可复用组件
│   │   ├── api/             # API 调用封装
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── composables/     # Vue 组合式函数
│   │   └── router/          # Vue Router 配置
│   └── package.json   # 前端依赖配置
└── README.md          # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
git clone https://github.com/lgy1027/ai-trending.git
cd ai-trending
```

### 2. 配置环境变量

复制后端和前端的 `.env.example` 文件为 `.env`，并填入您的 LLM 服务凭证：

```bash
# 后端配置
cp backend/.env.example backend/.env

# 前端配置
cp frontend/.env.example frontend/.env
```

编辑 `backend/.env` 文件：

```env
# .env
LLM_API_KEY="your_api_key"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4-turbo"
```

### 3. 运行项目

#### 方式一：使用 Docker（推荐）

```bash
docker compose up
```

#### 方式二：本地运行

安装后端依赖：

```bash
cd backend
pip install -r requirements.txt
```

启动后端服务：

```bash
# 运行完整服务（Web API + 定时任务）- 推荐
python app.py

# 仅运行 Web API 服务（用于前端开发）
python app.py --mode web --debug

# 仅运行定时报告生成器
python app.py --mode reporter

# 自定义端口和地址
python app.py --host 0.0.0.0 --port 5001 --debug
```

安装并启动前端（如需前端界面）：

```bash
cd frontend
npm install
npm run dev
```

访问地址：

- **后端 API**: `http://127.0.0.1:5001`
- **前端界面**: `http://127.0.0.1:5173`

## ⚙️ 详细配置

### 环境变量 (`.env`)

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `LLM_API_KEY` | ✅ | - | 大语言模型服务的 API Key |
| `LLM_BASE_URL` | ✅ | - | 大语言模型服务的基础 URL |
| `LLM_MODEL` | ❌ | `gpt-4-turbo` | 使用的模型 |
| `GITHUB_API_TOKEN` | ❌ | - | GitHub API Token（可选，获取更详细项目信息） |
| `SCHEDULE_TIME` | ❌ | `09:00` | 每日任务执行时间 (HH:MM) |
| `NUM_PROJECTS_TO_SUMMARIZE` | ❌ | `8` | 每日需要分析的新项目数量 |
| `MAX_PROJECTS_TO_SCRAPE` | ❌ | `25` | 从 Trending 列表中筛选的项目总数 |
| `TRENDING_DATE_RANGE` | ❌ | `daily` | 抓取时间范围：`daily`/`weekly`/`monthly` |

### 运行模式

通过 `--mode` 参数指定：

| 模式 | 说明 |
|------|------|
| `full` | 运行完整服务（Web API + 定时任务）[默认] |
| `web` | 仅运行 Web API 服务（适用于前端开发） |
| `reporter` | 仅运行定时报告生成任务（适用于后台运行） |

其他常用参数：

- `--host`: Web 服务监听地址，默认 `127.0.0.1`
- `--port`: Web 服务端口，默认 `5001`
- `--debug`: 启用调试模式

## 🤝 贡献

欢迎任何形式的贡献！如果您有好的想法或发现了 Bug，请随时提出 Issue 或提交 Pull Request。

## 公众号

欢迎关注我的公众号，获取实时技术解析及前沿观察。

<img src="images/wechat.png" width="300" height="300">

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。
