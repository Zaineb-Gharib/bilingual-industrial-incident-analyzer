"""Strict JSON parsing with one auditable Markdown-fence normalization."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParseResult:
    value: dict[str, Any] | None
    error: str | None
    normalization_applied: bool = False


_FENCE = re.compile(r"^\x60\x60\x60(?:json)?\s*(.*?)\s*\x60\x60\x60$", re.DOTALL | re.IGNORECASE)


def parse_json_object(raw: str, allow_single_fence: bool = True) -> ParseResult:
    text = raw.strip()
    if not text:
        return ParseResult(None, "response is empty")
    normalized = False
    if allow_single_fence:
        match = _FENCE.fullmatch(text)
        if match:
            text = match.group(1).strip()
            normalized = True
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        return ParseResult(None, f"{exc.msg} at line {exc.lineno} column {exc.colno}", normalized)
    if not isinstance(value, dict):
        return ParseResult(None, "top-level JSON value must be an object", normalized)
    return ParseResult(value, None, normalized)
