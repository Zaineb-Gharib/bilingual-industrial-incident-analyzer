"""Validate dataset schema, balance, evidence, split, leakage, and prompt examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.dataset_loader import (  # noqa: E402
    dataset_sha256,
    load_dataset,
    load_few_shot_ids,
    validate_dataset,
)


def main() -> None:
    dataset_path = ROOT / "data/incidents_v1.jsonl"
    examples_path = ROOT / "prompts/examples_v1.json"
    records = load_dataset(dataset_path)
    summary = validate_dataset(records, load_few_shot_ids(examples_path))
    summary["sha256"] = dataset_sha256(dataset_path)
    summary["human_review_status"] = "pending_manual_review"
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
