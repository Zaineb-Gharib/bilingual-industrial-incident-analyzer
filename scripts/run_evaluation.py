#!/usr/bin/env python3
"""Run or resume a frozen evaluation batch from the command line."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings  # noqa: E402
from src.domain.enums import DatasetSplit  # noqa: E402
from src.evaluation.dataset_loader import load_dataset  # noqa: E402
from src.services.batch_service import BatchService, estimated_semantic_calls  # noqa: E402
from src.services.factory import build_analysis_service  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--split", choices=[item.value for item in DatasetSplit], default="development"
    )
    parser.add_argument("--max-new-tasks", type=int, default=None)
    parser.add_argument(
        "--language-path",
        action="append",
        choices=["en->en", "en->zh", "zh->en", "zh->zh"],
        dest="language_paths",
    )
    parser.add_argument("--approve-live-batch", action="store_true")
    parser.add_argument("--notes", default="CLI evaluation")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env(ROOT)
    settings = replace(
        settings,
        provider=args.provider or settings.provider,
        model=args.model or settings.model,
    )
    if settings.provider != "demo" and not args.approve_live_batch:
        raise SystemExit(
            "Refusing live batch. Review provider pricing, run two small live tests, then pass "
            "--approve-live-batch explicitly."
        )
    records = load_dataset(settings.dataset_path)
    service = build_analysis_service(settings, settings.provider)
    batch = BatchService(settings, service, service.repository)
    manifest, tasks = batch.prepare(
        records,
        DatasetSplit(args.split),
        notes=args.notes,
        language_paths=set(args.language_paths) if args.language_paths else None,
    )
    print(
        json.dumps(
            {
                "run_id": manifest.run_id,
                "outputs": len(tasks),
                "base_semantic_calls": estimated_semantic_calls(tasks),
                "provider": manifest.provider,
                "model": manifest.model,
            },
            indent=2,
        )
    )

    def progress(done: int, total: int, _outcome: object) -> None:
        print(f"completed={done}/{total}")

    batch.run(
        manifest,
        tasks,
        records,
        live_batch_approved=args.approve_live_batch,
        progress=progress,
        max_new_tasks=args.max_new_tasks,
    )
    row = service.repository.get_run(manifest.run_id)
    print(json.dumps(row, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
