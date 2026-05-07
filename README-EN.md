# GitHub Trending Reporter 🚀

[English](./README-EN.md) | [简体中文](./README.md)

**An automated bot that analyzes GitHub Trending, curates daily selections, and generates tech insight reports for you.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Backend-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Framework](https://img.shields.io/badge/Frontend-Vue.js-blue.svg)](https://vuejs.org/)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)

---

## ✨ Features

- **📈 Daily Tracking & Analysis**: Automatically fetches the latest trending projects from GitHub and performs in-depth analysis using Large Language Models (LLM), generating "one-sentence reviews," "technical highlights," and "potential impact" insights.
- **🌐 Interactive Web Interface**: Modern Vue.js-based frontend with beautiful report browsing, search, and filtering capabilities, supporting responsive design.
- **🚀 Multi-dimensional Data Analysis**: Built-in trend analysis dashboard featuring "most frequent trending projects," "popular programming languages distribution," "fastest growing star projects," and "tech domain analysis."
- **⚙️ Highly Configurable**: Almost all core parameters (LLM model, API endpoints, scraping frequency, report quantity, etc.) can be easily configured via environment variables.
- **📦 Out-of-the-box Deployment**: Docker support for one-click deployment without complex environment configuration, supporting multiple running modes (full service, web-only, reporter-only).
- **💾 Data Persistence**: Uses SQLite database to store historical data, avoiding duplicate analysis and supporting trend analysis features.

## 📊 Output Example

The project generates daily reports in the `output` directory.

### Markdown Report (`.md`)

A clean, structured Markdown file suitable for direct publishing on various platforms.

```markdown
## 🚀 The AI wave continues to sweep, and today GitHub is buzzing with several game-changing open-source models!

### ✨ awesome-project

**One-Sentence Review**: A revolutionary tool that solves a major pain point in the X domain.
**💡 Tech Highlights & Innovations**: It utilizes the latest A technology and B framework, with a particularly clever C design pattern.
**📈 Potential Impact & Applications**: Poised to set a new standard in the Y industry, especially suitable for X, Y, and Z scenarios.
**🔗 Project Link**: [awesome-project](https://github.com/user/awesome-project)

---

### ✨ another-cool-repo

**One-Sentence Review**: ...
...
```

![Markdown Example](images/image.png)

### Interactive Web UI

An HTML file with a modern, card-based design for a better visual reading experience.

![Web UI Example](images/web.png)

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask
- **Frontend**: Vue.js 3, TypeScript, Vite, Pinia, TailwindCSS
- **Data Scraping**: `requests`, `BeautifulSoup4`
- **AI Integration**: `openai`
- **Task Scheduling**: `schedule`
- **Database**: `SQLite`
- **Deployment**: `Docker`

## 📁 Project Structure

The project adopts a frontend-backend separation architecture:

```
├── backend/           # Backend code directory
│   ├── app.py         # Main program entry (supports 3 running modes)
│   ├── router.py      # API route definitions
│   ├── config/        # Configuration module
│   │   ├── settings.py      # Environment variables configuration
│   │   └── logging_config.py
│   ├── app/           # Core functionality modules
│   │   ├── analyzer.py      # Data analysis functionality
│   │   ├── summarizer.py    # AI summary generation
│   │   ├── scraper.py       # GitHub data scraping
│   │   ├── database.py      # Database operations
│   │   ├── github_api.py    # GitHub API calls
│   │   ├── file_writer.py   # Report file output
│   │   ├── cache.py         # IP rate limiting
│   │   └── main.py          # Task execution entry point
│   └── routes/        # Blueprint route modules
│       ├── projects.py      # Project-related APIs
│       ├── stats.py         # Statistics-related APIs
│       └── common.py        # Common APIs
├── frontend/          # Frontend code directory
│   ├── src/           # Vue.js source code
│   │   ├── views/           # Page views
│   │   ├── components/      # Reusable components
│   │   ├── api/             # API call encapsulation
│   │   ├── stores/          # Pinia state management
│   │   ├── composables/     # Vue composables
│   │   └── router/          # Vue Router configuration
│   └── package.json   # Frontend dependency configuration
└── README.md          # Project documentation
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/lgy1027/ai-trending.git
cd ai-trending
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` in both backend and frontend directories:

```bash
# Backend configuration
cp backend/.env.example backend/.env

# Frontend configuration
cp frontend/.env.example frontend/.env
```

Edit the `backend/.env` file:

```env
# .env
LLM_API_KEY="your_api_key"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4-turbo"
```

### 3. Run the Project

#### Method 1: Using Docker (Recommended)

```bash
docker compose up
```

#### Method 2: Running Locally

Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Start the backend service:

```bash
# Run full service (Web API + scheduled tasks) - Recommended
python app.py

# Run only Web API service (for frontend development)
python app.py --mode web --debug

# Run only scheduled report generator
python app.py --mode reporter

# Custom host and port
python app.py --host 0.0.0.0 --port 5001 --debug
```

Install and start the frontend (if you need the web interface):

```bash
cd frontend
npm install
npm run dev
```

Access URLs:

- **Backend API**: `http://127.0.0.1:5001`
- **Frontend Interface**: `http://127.0.0.1:5173`

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_KEY` | ✅ | - | Large Language Model service API Key |
| `LLM_BASE_URL` | ✅ | - | Base URL for LLM service |
| `LLM_MODEL` | ❌ | `gpt-4-turbo` | Model to use |
| `GITHUB_API_TOKEN` | ❌ | - | GitHub API Token (optional, for more detailed project info) |
| `SCHEDULE_TIME` | ❌ | `09:00` | Daily task execution time (HH:MM) |
| `NUM_PROJECTS_TO_SUMMARIZE` | ❌ | `8` | Number of new projects to analyze daily |
| `MAX_PROJECTS_TO_SCRAPE` | ❌ | `25` | Number of projects to filter from Trending list |
| `TRENDING_DATE_RANGE` | ❌ | `daily` | Scrape time range: `daily`/`weekly`/`monthly` |

### Running Modes

Specify via the `--mode` parameter:

| Mode | Description |
|------|-------------|
| `full` | Run full service (Web API + scheduled tasks) [Default] |
| `web` | Run only Web API service (for frontend development) |
| `reporter` | Run only scheduled report generator (for background running) |

Other common parameters:

- `--host`: Web service listening address, default `127.0.0.1`
- `--port`: Web service port, default `5001`
- `--debug`: Enable debug mode

## 🤝 Contributing

Contributions of any kind are welcome! If you have a great idea or find a bug, feel free to open an Issue or submit a Pull Request.

## WeChat

Welcome to follow me for real-time technical analysis and cutting-edge news.

<img src="images/wechat.png" width="300" height="300">

## 📄 License

This project is licensed under the [MIT License](LICENSE).
