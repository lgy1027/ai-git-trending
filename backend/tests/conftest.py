"""Shared pytest fixtures for the backend test suite.

Note: env vars must be set at import time (before `config.settings` is loaded)
so that the test process uses an isolated tmp DB / report dir.
"""

from __future__ import annotations

import os
import tempfile

_tmp_root = tempfile.mkdtemp(prefix="ai_trending_test_")
os.environ.setdefault("OUTPUT_DIR", _tmp_root)
os.environ.setdefault("DB_PATH", os.path.join(_tmp_root, "test.db"))
os.environ.setdefault("MD_DIR", os.path.join(_tmp_root, "md"))
os.environ.setdefault("HTML_DIR", os.path.join(_tmp_root, "html"))

import pytest  # noqa: E402  (env vars must be set before this)


@pytest.fixture
def app():
    """Flask app fixture with isolated config."""

    from router import app as flask_app

    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client."""

    return app.test_client()