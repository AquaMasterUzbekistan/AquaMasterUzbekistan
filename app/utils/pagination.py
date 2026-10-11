"""Pagination utility for inline keyboard pages."""

from __future__ import annotations

import math
from typing import Any


class Paginator:
    """Handles pagination of query results."""

    def __init__(self, items: list[Any], page: int = 1, per_page: int = 8):
        self.items = items
        self.page = max(1, page)
        self.per_page = per_page
        self.total = len(items)
        self.total_pages = max(1, math.ceil(self.total / self.per_page))
        self.page = min(self.page, self.total_pages)

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def page_items(self) -> list[Any]:
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]

    @property
    def page_info(self) -> str:
        return f"📄 {self.page}/{self.total_pages}"
