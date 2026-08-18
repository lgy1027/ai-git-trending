# GitHub Trending Reporter

> Automatically scrape GitHub Trending every day, run LLM deep analysis, and produce structured technology insight reports.

[简体中文](./README.md) · English

[![License: MIT](https://img.shields.io/github/license/lgy1027/ai-git-trending)](LICENSE)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/vue-3-brightgreen.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![GitHub stars](https://img.shields.io/github/stars/lgy1027/ai-git-trending)](https://github.com/lgy1027/ai-git-trending/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/lgy1027/ai-git-trending)](https://github.com/lgy1027/ai-git-trending/network)

Every day at 09:00 (configurable), it automatically scrapes trending GitHub projects, asks an LLM to generate three-part analysis — "one-line review / tech highlights / potential impact" — stores the results in SQLite, and produces Markdown / HTML reports. It also provides an interactive web dashboard for browsing historical trends and favoriting interesting projects.

![Home overview](images/web.png)

## Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Docker Deployment](#-docker-deployment)
- [Configuration](#-configuration)
- [Run Modes](#-run-modes)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

## ✨ Features

### 🤖 Automated Pipeline
- Daily scheduled GitHub Trending scrape (daily / weekly / monthly selectable)
- Automatic LLM calls to generate "one-line review, tech highlights, potential impact" three-part analysis
- Output Markdown / HTML dual-format reports, cleanly structured, ready to copy into blog posts or newsletters

### 📊 Interactive Web Dashboard
- Dark sci-fi styled interface powered by Vue 3 + TypeScript + Tailwind
- Multi-dimensional visualizations: rankings, trend graphs, tech domain classification
- Auto health check of the backend every day (badge shows online status)
- Favorite interesting projects (based on localStorage + anonymous client_id, no login required)

### 🔍 Deep Analysis
- Click any project to open the detail view and expand the full LLM-generated deep analysis report
- Auto-sliced from the day's Markdown report — no need to read the whole thing

### ⚙️ Highly Configurable
- LLM model, API endpoint, scrape period, analysis count, scrape count all read from environment variables
- Works with any OpenAI-compatible service (OpenAI / DeepSeek / Tongyi Qianwen / self-hosted)

### 🐳 One-Command Deployment
- Docker Compose config shipped out of the box — clone and run with two commands
- Multiple run modes: full service / web-only / reporter-only

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- An OpenAI-compatible LLM service (API Key + Base URL)

### 1. Clone the project

```bash
git clone https://github.com/lgy1027/ai-git-trending.git
cd ai-git-trending
```

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edit `backend/.env` and at minimum fill in:

```env
LLM_API_KEY="sk-your_api_key_here"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4-turbo"
```

`frontend/.env` generally needs no changes (defaults to local backend).

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
python app.py --mode web --port 5001 --debug
```

The backend will start at `http://127.0.0.1:5001`.

### 4. Start the frontend (optional, new shell)

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at `http://localhost:5173`. Vite automatically proxies `/api` and `/images` requests to the backend.

Open your browser at `http://localhost:5173` and hover over "Contact Us" in the top nav to see the WeChat QR code.

## 🐳 Docker Deployment

The fastest path, suitable for production / continuous runs:

```bash
# 1. Configure .env (same as above)
cp backend/.env.example backend/.env
# Edit backend/.env and fill in LLM_API_KEY etc.

# 2. Start with one command
docker compose up -d

# 3. View logs
docker compose logs -f backend
```

Once it's running:
- Web API: `http://<your-host>:5001`
- Reports: persisted in the `backend/output/` directory

## ⚙️ Configuration

### Backend environment variables (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `LLM_API_KEY` | ✅ | - | LLM service API Key |
| `LLM_BASE_URL` | ✅ | - | LLM service Base URL (OpenAI-compatible) |
| `LLM_MODEL` | ❌ | `gpt-4-turbo` | Model name |
| `GITHUB_API_TOKEN` | ❌ | - | GitHub Token (optional, raises rate limit) |
| `SCHEDULE_TIME` | ❌ | `09:00` | Daily job time (HH:MM) |
| `NUM_PROJECTS_TO_SUMMARIZE` | ❌ | `8` | Number of new projects analyzed per day |
| `MAX_PROJECTS_TO_SCRAPE` | ❌ | `25` | Total projects filtered from Trending |
| `TRENDING_DATE_RANGE` | ❌ | `daily` | Scrape period: `daily` / `weekly` / `monthly` |
| `PORT` | ❌ | `5001` | Web service port |
| `OUTPUT_DIR` | ❌ | `./output` | Report output directory |
| `SCRAPER_RETRY_TOTAL` | ❌ | `3` | Retry count on scrape failure |
| `SCRAPER_PROJECT_INTERVAL` | ❌ | `1` | Delay between project requests (seconds) |

Full list see `backend/config/settings.py`.

### Frontend environment variables (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:5001
```

## 🎛 Run Modes

```bash
python app.py --mode <mode> [--host 0.0.0.0] [--port 5001] [--debug]
```

| Mode | Description |
|---|---|
| `full` | Web API + scheduled job together (**default**) |
| `web` | Web API only, no scheduled job (good for frontend dev) |
| `reporter` | Scheduled job only, no Web (good for pure background scraping) |

## 📡 API Reference

All backend APIs are mounted under the `/api/` prefix. See [`backend/router.py`](backend/router.py) for full detail.

| Path | Description |
|---|---|
| `GET /api/reports` | List of reports |
| `GET /api/report/<date>` | Report content for a specific date |
| `GET /api/projects/<date>` | Project list for a specific date |
| `GET /api/project/<name>` | Project details |
| `GET /api/project/<name>/analysis` | Single-project AI deep analysis slice |
| `GET /api/trends?days=7` | Trend data (7 / 30 / 182 / 365 days) |
| `GET /api/stats` | Statistics |
| `GET /api/language-distribution` | Language distribution |
| `GET /api/tech-domains?days=7` | Tech domain classification |
| `GET /api/favorites?client_id=xxx` | List favorites |
| `POST /api/favorites` | Add favorite |
| `DELETE /api/favorites` | Remove favorite |
| `GET /api/rate-limit-status` | Current IP rate-limit status |
| `GET /api/download/<date>/<md\|html>` | Download report (rate-limited) |
| `GET /health` | Health check |

## 🧪 Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

Current test coverage:
- LLM prompt rendering (`prompts/`)
- Scraper retry behavior (with mocks)
- System routes (health check, rate limiting)

## 🗺 Roadmap

- [ ] Project detail page supports deep link sharing (with OG meta)
- [ ] Rankings support "time range + domain" combined filtering
- [ ] Report PDF export
- [ ] More LLM providers (Anthropic / Gemini)
- [ ] Pluggable tech domain classification (user-customizable)

## 🤝 Contributing

All forms of contribution are welcome:

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Before submitting, please run `pytest` to make sure existing tests pass.

## 📜 License

This project is open-sourced under the [MIT License](LICENSE).

## 📮 Contact

- 🐛 Bug / suggestion: [GitHub Issues](https://github.com/lgy1027/ai-git-trending/issues)
- 💬 WeChat group: see QR code below
- 🔗 Project home: [lgy1027/ai-git-trending](https://github.com/lgy1027/ai-git-trending)

<p align="center">
  <img src="images/wechat.png" alt="WeChat QR" width="220" />
  <br />
  <sub>Scan the WeChat QR and mention "GitTrend" for a faster reply</sub>
</p>

---

⭐ If this project helps you, a Star would be appreciated!