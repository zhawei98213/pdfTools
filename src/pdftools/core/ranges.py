"""Utilities for parsing user-supplied page ranges."""
from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


Range = Tuple[int, int]


def parse_page_ranges(expression: str, total_pages: int) -> List[Range]:
    """Parse ranges like ``"1-3,7,9-"`` into an ordered list of (start, end)."""

    expr = (expression or "").strip().lower()
    if not expr or expr == "all":
        return [(1, total_pages)]

    ranges: list[Range] = []
    for chunk in expr.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_text, end_text = chunk.split("-", 1)
            start = _parse_page_number(start_text, default=1)
            end = _parse_page_number(end_text, default=total_pages)
        else:
            value = _parse_page_number(chunk)
            start = end = value
        if start < 1 or end < 1:
            raise ValueError("Page numbers must be positive")
        if start > end:
            raise ValueError(f"Invalid range: {chunk}")
        if end > total_pages:
            raise ValueError("Range exceeds total page count")
        ranges.append((start, end))

    return _merge_adjacent_ranges(ranges)


def _parse_page_number(text: str, default: int | None = None) -> int:
    value = (text or "").strip()
    if not value:
        if default is None:
            raise ValueError("Missing page number")
        return default
    if not value.isdigit():
        raise ValueError(f"Invalid page number: {value}")
    return int(value)


def _merge_adjacent_ranges(ranges: Sequence[Range]) -> list[Range]:
    ordered = sorted(ranges)
    merged: list[Range] = []
    for start, end in ordered:
        if not merged:
            merged.append((start, end))
            continue
        prev_start, prev_end = merged[-1]
        if start <= prev_end + 1:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged
