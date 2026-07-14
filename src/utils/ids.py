"""Stable and random identifiers used by services and batch resume."""

from __future__ import annotations

import hashlib
import uuid


def random_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(parts).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(payload).hexdigest()[:20]}"
