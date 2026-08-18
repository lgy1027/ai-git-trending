"""Tests for the prompt template loader and the build_*_prompt helpers."""

from __future__ import annotations

from app.summarizer import (
    build_entity_prompt,
    build_overview_prompt,
    build_overview_retry_prompt,
    build_project_prompt,
    build_project_retry_prompt,
)
from prompts import load_prompt, render_prompt


def _sample_project():
    return {
        "name": "owner/repo",
        "url": "https://github.com/owner/repo",
        "description": "A demo project",
        "language": "Python",
        "stars": 1234,
        "forks": 56,
        "contributor_count": 7,
        "open_issues": 3,
        "watchers": 89,
        "created_at": "2024-01-01",
        "updated_at": "2025-01-01",
        "readme_content": "Some README text here.",
    }


def test_load_prompt_returns_non_empty_string():
    content = load_prompt("overview")
    assert isinstance(content, str)
    assert "{project_details}" in content


def test_load_prompt_rejects_unknown_name():
    import pytest

    with pytest.raises(ValueError):
        load_prompt("does_not_exist")


def test_render_prompt_substitutes_placeholders():
    rendered = render_prompt("overview", project_details="- foo: bar")
    assert "- foo: bar" in rendered
    assert "{project_details}" not in rendered


def test_build_overview_prompt_includes_projects():
    projects = [
        {"name": "a/b", "description": "desc A"},
        {"name": "c/d", "description": "desc B"},
    ]
    prompt = build_overview_prompt(projects)
    assert "- a/b: desc A" in prompt
    assert "- c/d: desc B" in prompt


def test_build_overview_retry_prompt_includes_projects():
    projects = [{"name": "x/y", "description": "desc"}]
    prompt = build_overview_retry_prompt(projects)
    assert "- x/y: desc" in prompt


def test_build_project_prompt_includes_all_fields():
    project = _sample_project()
    prompt = build_project_prompt(project)
    assert "owner/repo" in prompt
    assert "https://github.com/owner/repo" in prompt
    assert "Python" in prompt
    assert "1234" in prompt
    # The "url" placeholder appears twice in the template; both must be filled.
    assert prompt.count("{url}") == 0


def test_build_project_prompt_handles_missing_optional_fields():
    project = {"name": "owner/repo"}
    prompt = build_project_prompt(project)
    assert "owner/repo" in prompt
    assert "{name}" not in prompt


def test_build_project_retry_prompt_includes_core_fields():
    project = _sample_project()
    prompt = build_project_retry_prompt(project)
    assert "owner/repo" in prompt
    assert "{name}" not in prompt


def test_build_entity_prompt_includes_owner_and_details():
    entity = {
        "name": "Acme",
        "type": "Organization",
        "bio": "We build things",
        "created_at": "2020-01-01",
        "followers": 100,
        "public_repos": 42,
    }
    repos = [{"name": "acme/lib", "stars": 10, "language": "Go"}]
    prompt = build_entity_prompt("acme", entity, repos, "Go, Python")
    assert "Acme" in prompt
    assert "Organization" in prompt
    assert "We build things" in prompt
    assert "- acme/lib (10 stars, Go)" in prompt


def test_build_entity_prompt_falls_back_to_owner_for_missing_name():
    prompt = build_entity_prompt("acme", {}, [], "N/A")
    assert "acme" in prompt