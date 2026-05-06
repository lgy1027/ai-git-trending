"""Persist generated reports as Markdown and HTML."""

from __future__ import annotations

import os
import re
from datetime import datetime

import markdown as md

from config.logging_config import get_logger
from config.settings import HTML_DIR, HTML_TEMPLATE, MD_DIR

logger = get_logger("file_writer", "INFO")


def clean_markdown_content(content: str) -> str:
    if not content:
        return ""

    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE)
    cleaned = re.sub(r"(?im)^.*\bpotential output\b.*$", "", cleaned)
    cleaned = re.sub(r"(?im)^.*\blet'?s craft final answer\b.*$", "", cleaned)
    cleaned = re.sub(r"(?im)^.*\bfinal answer[:：]?\s*$", "", cleaned)
    cleaned = re.sub(r"(?im)^.*\banalysis[:：]?\s*$", "", cleaned)
    cleaned = re.sub(r"(?im)^```(?:markdown)?\s*$", "", cleaned)

    heading_match = re.search(r"(?m)^#{1,3}\s+.+$", cleaned)
    if heading_match:
        cleaned = cleaned[heading_match.start() :]

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def save_summary_files(summary_content: str):
    os.makedirs(MD_DIR, exist_ok=True)
    os.makedirs(HTML_DIR, exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    file_basename = f"github_trending_{today_str}"
    md_path = os.path.join(MD_DIR, f"{file_basename}.md")
    html_path = os.path.join(HTML_DIR, f"{file_basename}.html")

    title = f"GitHub 热门项目精选分析 ({today_str})"
    full_md_content = clean_markdown_content(summary_content)

    try:
        with open(md_path, "w", encoding="utf-8") as handle:
            handle.write(full_md_content)
        logger.info("Markdown report saved to %s", md_path)
    except OSError as exc:
        logger.error("Failed to write Markdown report: %s", exc)
        return

    try:
        html_body = md.markdown(full_md_content, extensions=["fenced_code", "tables"])
        final_html = HTML_TEMPLATE.format(title=title, content=f"<h1>{title}</h1>\n{html_body}")
        with open(html_path, "w", encoding="utf-8") as handle:
            handle.write(final_html)
        logger.info("HTML report saved to %s", html_path)
    except Exception as exc:
        logger.error("Failed to write HTML report: %s", exc)
