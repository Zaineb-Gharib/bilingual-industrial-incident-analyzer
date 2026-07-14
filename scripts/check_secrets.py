#!/usr/bin/env python3
"""Fail on likely committed credentials while allowing documented placeholders."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "work", "outputs", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".csv",
    ".example",
}
PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9/+_-]{24,}"),
]
ALLOW = {"your_api_key_here", "replace_me", "example_only"}


def main() -> None:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(value in line.lower() for value in ALLOW):
                continue
            if any(pattern.search(line) for pattern in PATTERNS):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}")
    if findings:
        raise SystemExit("Potential secrets found:\n" + "\n".join(findings))
    print("Secret scan passed: no likely credentials found in project text files.")


if __name__ == "__main__":
    main()
