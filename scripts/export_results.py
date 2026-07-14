#!/usr/bin/env python3
"""Export persisted analyses, metrics, and a blinded review sheet."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings  # noqa: E402
from src.evaluation.dataset_loader import load_dataset  # noqa: E402
from src.evaluation.manual_review import export_blinded_review_template  # noqa: E402
from src.storage.repositories import AnalysisRepository  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/processed")
    args = parser.parse_args()
    settings = Settings.from_env(ROOT)
    repository = AnalysisRepository(settings.database_path)
    run = repository.get_run(args.run_id)
    if not run:
        raise SystemExit(f"Unknown run: {args.run_id}")
    analyses = repository.list_analyses(args.run_id)
    metrics = repository.list_metrics(args.run_id)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    analysis_path = args.output_dir / f"{args.run_id}_analyses.csv"
    if analyses:
        with analysis_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(analyses[0]))
            writer.writeheader()
            writer.writerows(analyses)
    metric_path = args.output_dir / f"{args.run_id}_metrics.json"
    metric_path.write_text(
        json.dumps(
            [item.model_dump(mode="json") for item in metrics], ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    records = load_dataset(settings.dataset_path)
    gold = {item.scenario_id: item.model_dump(mode="json") for item in records}
    review_path = args.output_dir / f"{args.run_id}_manual_review.csv"
    export_blinded_review_template(analyses, gold, review_path)
    print(
        json.dumps(
            {
                "analyses": str(analysis_path),
                "metrics": str(metric_path),
                "review": str(review_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
