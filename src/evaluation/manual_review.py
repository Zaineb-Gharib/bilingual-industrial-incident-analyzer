"""Create blinded manual-review templates without modifying model outputs."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

REVIEW_COLUMNS = [
    "output_id",
    "source_report",
    "gold_json",
    "model_output_json",
    "affected_system_0_2",
    "symptoms_0_2",
    "suspected_cause_0_2",
    "immediate_actions_0_2",
    "long_term_actions_0_2",
    "evidence_0_2",
    "uncertainty_0_2",
    "output_language_quality_0_2",
    "factual_claim_units",
    "unsupported_claim_units",
    "dangerous_advice",
    "reviewer_id",
    "notes",
]


def export_blinded_review_template(
    rows: list[dict[str, Any]],
    gold_by_scenario: dict[str, dict[str, Any]],
    path: Path,
    seed: int = 20260714,
) -> None:
    randomized = list(rows)
    random.Random(seed).shuffle(randomized)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        for row in randomized:
            writer.writerow(
                {
                    "output_id": row.get("analysis_id"),
                    "source_report": row.get("raw_input") or "[not stored]",
                    "gold_json": json.dumps(
                        gold_by_scenario.get(str(row.get("scenario_id")), {}),
                        ensure_ascii=False,
                    ),
                    "model_output_json": row.get("parsed_response") or "",
                }
            )
