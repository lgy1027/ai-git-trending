"""Single source of truth for project tech-domain categories.

Used by:
- Prompt templates (`prompts/project.txt`, `prompts/project_retry.txt`) to instruct the LLM
- LLM output normalizer (`app/summarizer.py`) to map free-form answers to canonical labels
- API routes (`routes/stats.py`, `app/analyzer.py`) to enumerate the fixed category set

Keep this list in sync with the prompt template, otherwise the LLM will output
labels that fall back to ``Other`` after normalization.
"""

from __future__ import annotations

# Canonical domain list. Order is stable for UI display but not semantically meaningful.
TECH_DOMAINS: tuple[str, ...] = (
    "AI/ML",
    "LLM Apps",
    "Web",
    "Frontend",
    "Mobile",
    "DevOps",
    "Data Science",
    "Database",
    "Tools",
    "Security",
    "Blockchain",
    "Gaming",
    "OS",
    "IoT",
    "Other",
)


def tech_domains_for_prompt() -> str:
    """Return the comma-separated category list for injection into prompt templates."""
    return "、".join(TECH_DOMAINS)


__all__ = ["TECH_DOMAINS", "tech_domains_for_prompt"]
