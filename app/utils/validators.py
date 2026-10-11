"""Input validators."""

from __future__ import annotations

import re


def is_valid_scientific_name(name: str) -> bool:
    """Basic check for valid scientific name format."""
    # Should have at least genus + species, Latin chars
    parts = name.strip().split()
    if len(parts) < 2:
        return False
    return all(re.match(r"^[A-Za-z\-]+$", p) for p in parts[:2])


def sanitize_search_query(query: str) -> str:
    """Strip and normalize a search query."""
    q = query.strip()
    # Remove potential SQL injection characters
    q = re.sub(r"[;'\"\\\-\-]", "", q)
    return q[:200]  # Limit length


def is_positive_number(value: str) -> bool:
    """Check if value is a positive number."""
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False


def validate_telegram_id(tid: int) -> bool:
    """Telegram IDs are positive integers."""
    return isinstance(tid, int) and tid > 0
