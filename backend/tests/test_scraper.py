"""Tests for the scraper's HTTP session: retry adapter, shared UA, singleton."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app import scraper


def test_session_has_custom_user_agent():
    assert "ai-git-trending" in scraper._session.headers["User-Agent"]


def test_session_mounts_retry_adapter_on_both_schemes():
    for scheme in ("https://", "http://"):
        adapter = scraper._session.get_adapter(scheme + "github.com")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == 3
        assert 503 in adapter.max_retries.status_forcelist


def test_session_is_a_module_level_singleton():
    # Re-importing should not rebuild the session.
    from app import scraper as scraper_again

    assert scraper._session is scraper_again._session


def test_scrape_returns_none_on_request_failure():
    with patch.object(scraper._session, "get", side_effect=requests.RequestException("boom")):
        assert scraper.scrape_github_trending() is None


def test_scrape_returns_repo_list_on_success():
    html = """
    <html><body>
      <article class="Box-row">
        <h2 class="h3"><a href="/owner/sample">owner / sample</a></h2>
        <p class="col-9">A sample project</p>
      </article>
    </body></html>
    """

    response = MagicMock()
    response.text = html
    response.raise_for_status = MagicMock()

    with patch.object(scraper._session, "get", return_value=response), patch(
        "app.scraper.get_repo_details", return_value=None
    ):
        result = scraper.scrape_github_trending()

    assert result is not None
    assert len(result) == 1
    repo = result[0]
    assert repo["name"] == "owner/sample"
    assert repo["url"] == "https://github.com/owner/sample"
    assert repo["description"] == "A sample project"
    assert repo["language"] == "N/A"
    # Stars / forks fall back to 0 when both API and scraping paths miss.
    assert repo["stars"] == 0
    assert repo["forks"] == 0