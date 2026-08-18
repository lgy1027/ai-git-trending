"""Prompt template loader.

Each template is a plain `.txt` file with `{placeholder}` fields filled by
`str.format(**kwargs)`. Templates are cached after the first read.
"""

from __future__ import annotations

import functools
import os
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent

_VALID_NAMES = {
    "overview",
    "overview_retry",
    "project",
    "project_retry",
    "entity",
}


@functools.lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """Read a prompt template by name (without extension)."""

    if name not in _VALID_NAMES:
        raise ValueError(f"Unknown prompt template: {name!r}")

    path = _PROMPTS_DIR / f"{name}.txt"
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def render_prompt(template_name: str, **kwargs) -> str:
    """Load a template and substitute placeholders."""

    template = load_prompt(template_name)
    return template.format(**kwargs)


__all__ = ["load_prompt", "render_prompt"]