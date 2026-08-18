import time

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.github_api import get_repo_details
from config.logging_config import get_logger
from config.settings import (
    GITHUB_TRENDING_URL,
    MAX_PROJECTS_TO_SCRAPE,
    SCRAPER_BACKOFF_FACTOR,
    SCRAPER_PROJECT_INTERVAL,
    SCRAPER_RETRY_TOTAL,
    SCRAPER_USER_AGENT,
)

logger = get_logger("scraper", "INFO")


def _build_session() -> requests.Session:
    """Create a shared requests.Session with automatic retries on transient errors."""

    session = requests.Session()
    session.headers.update({"User-Agent": SCRAPER_USER_AGENT})

    retry = Retry(
        total=SCRAPER_RETRY_TOTAL,
        backoff_factor=SCRAPER_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True,
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


_session = _build_session()


def scrape_github_trending():
    logger.info(f"⏳ Fetching top {MAX_PROJECTS_TO_SCRAPE} projects from GitHub Trending...")
    try:
        response = _session.get(GITHUB_TRENDING_URL, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"❌ Error fetching GitHub page: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    repo_list = []
    for repo_element in soup.find_all("article", class_="Box-row")[:MAX_PROJECTS_TO_SCRAPE]:
        title_element = repo_element.find("h2", class_="h3")
        if not title_element:
            continue

        repo_name_raw = title_element.get_text(strip=True)
        # A more robust way to clean the repo name: remove all whitespace and then replace the slash.
        repo_name = "".join(repo_name_raw.split()).replace("/", "/")
        repo_url = "https://github.com" + title_element.find("a")["href"]
        # The repo name for the API call should be extracted directly from the URL
        # to ensure it's always correct.
        api_repo_name = "/".join(repo_url.split("/")[-2:])

        logger.info(f"🔍 Processing repository: {repo_name}")

        # Scrape basic info
        description_element = repo_element.find("p", class_="col-9")
        scraped_description = description_element.get_text(strip=True) if description_element else "No description provided."

        language_element = repo_element.find("span", itemprop="programmingLanguage")
        scraped_language = language_element.get_text(strip=True) if language_element else "N/A"

        # Fetch detailed info from GitHub API
        api_details = get_repo_details(api_repo_name)

        if api_details:
            logger.info(f"API details fetched for {repo_name}")
            # Combine scraped data with API data
            repo_data = {
                "name": repo_name,
                "url": repo_url,
                "description": api_details.get("description", scraped_description),
                "language": api_details.get("language", scraped_language),
                "stars": api_details.get("stars", 0),
                "forks": api_details.get("forks", 0),
                "tags": api_details.get("tags", []),
                "created_at": api_details.get("created_at"),
                "updated_at": api_details.get("updated_at"),
                "open_issues": api_details.get("open_issues", 0),
                "watchers": api_details.get("watchers", 0),
                "contributor_count": api_details.get("contributor_count", 0),
                "readme_content": api_details.get("readme_content", ""),
            }
        else:
            # Fallback to scraped data if API fails
            logger.warning(f"API details fetch failed for {repo_name}, using scraped data as fallback.")
            star_element = repo_element.find("a", href=f"{repo_url.replace('https://github.com','').strip()}/stargazers")
            repo_stars = 0
            if star_element:
                try:
                    repo_stars = int(star_element.get_text(strip=True).replace(",", ""))
                except (ValueError, TypeError):
                    repo_stars = 0

            fork_element = repo_element.find("a", href=f"{repo_url.replace('https://github.com','').strip()}/forks")
            repo_forks = 0
            if fork_element:
                try:
                    repo_forks = int(fork_element.get_text(strip=True).replace(",", ""))
                except (ValueError, TypeError):
                    repo_forks = 0

            repo_data = {
                "name": repo_name,
                "url": repo_url,
                "description": scraped_description,
                "language": scraped_language,
                "stars": repo_stars,
                "forks": repo_forks,
                "tags": [],
                "created_at": None,
                "updated_at": None,
                "open_issues": "N/A",
                "watchers": "N/A",
                "contributor_count": "N/A",
            }

        repo_list.append(repo_data)
        time.sleep(SCRAPER_PROJECT_INTERVAL)  # Respect API rate limits

    logger.info(f"✅ Successfully processed {len(repo_list)} repositories.")
    return repo_list