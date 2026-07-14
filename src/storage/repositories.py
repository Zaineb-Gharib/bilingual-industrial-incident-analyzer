"""Append-oriented repositories for analyses, attempts, runs, and metrics."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.domain.models import AnalysisOutcome, AttemptRecord
from src.schemas.run_records import ManualReviewRecord, MetricRecord, RunManifest
from src.storage.database import connect
from src.utils.text import text_hash


class AnalysisRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.connection = connect(database_path)

    def close(self) -> None:
        self.connection.close()

    def save_attempt(self, attempt: AttemptRecord) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO attempt_records (
                    attempt_id, analysis_id, stage, transport_attempt, started_at,
                    finished_at, latency_ms, provider, model, raw_response,
                    error_type, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt.attempt_id,
                    attempt.analysis_id,
                    attempt.stage.value,
                    attempt.transport_attempt,
                    attempt.started_at.isoformat(),
                    attempt.finished_at.isoformat(),
                    attempt.latency_ms,
                    attempt.provider,
                    attempt.model,
                    attempt.raw_response,
                    attempt.error_type,
                    attempt.error_message,
                ),
            )

    def save_outcome(self, outcome: AnalysisOutcome, raw_input: str | None) -> None:
        parsed_model = outcome.result or outcome.validation.parsed
        parsed = (
            json.dumps(parsed_model.model_dump(mode="json"), ensure_ascii=False)
            if parsed_model
            else None
        )
        issues = json.dumps(
            [issue.model_dump(mode="json") for issue in outcome.validation.issues],
            ensure_ascii=False,
        )
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO analysis_records (
                    analysis_id, correlation_id, run_id, task_id, dataset_version,
                    scenario_id, provider, model, strategy, prompt_version, prompt_hash,
                    schema_version, input_language, output_language, created_at,
                    latency_ms, retry_count, semantic_call_count, validation_status,
                    failure_type, input_hash, raw_input, initial_raw_response,
                    final_raw_response, repair_raw_response, parsed_response,
                    validation_issues, first_pass_json_valid, repair_assisted_valid,
                    final_accepted_valid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    outcome.analysis_id,
                    outcome.correlation_id,
                    outcome.request.run_id,
                    outcome.request.task_id,
                    outcome.request.dataset_version,
                    outcome.request.scenario_id,
                    outcome.provider,
                    outcome.model,
                    outcome.request.strategy.value,
                    outcome.prompt_version,
                    outcome.prompt_hash,
                    "1.0",
                    outcome.detected_input_language.value,
                    outcome.request.output_language.value,
                    outcome.created_at.isoformat(),
                    outcome.total_latency_ms,
                    outcome.retry_count,
                    outcome.semantic_call_count,
                    outcome.validation.status.value,
                    outcome.failure_type.value,
                    text_hash(outcome.request.incident_text),
                    raw_input,
                    outcome.initial_raw_response,
                    outcome.final_raw_response,
                    outcome.repair_raw_response,
                    parsed,
                    issues,
                    int(outcome.first_pass_json_valid),
                    int(outcome.repair_assisted_valid),
                    int(outcome.final_accepted_valid),
                ),
            )

    def list_analyses(self, run_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM analysis_records"
        params: tuple[Any, ...] = ()
        if run_id:
            query += " WHERE run_id = ?"
            params = (run_id,)
        query += " ORDER BY created_at"
        return [dict(row) for row in self.connection.execute(query, params).fetchall()]

    def completed_task_ids(self, run_id: str) -> set[str]:
        rows = self.connection.execute(
            "SELECT task_id FROM analysis_records WHERE run_id = ? AND task_id IS NOT NULL",
            (run_id,),
        ).fetchall()
        return {str(row["task_id"]) for row in rows}

    def create_run(self, manifest: RunManifest) -> None:
        now = datetime.now(UTC).isoformat()
        with self.connection:
            self.connection.execute(
                """
                INSERT OR IGNORE INTO batch_runs (
                    run_id, manifest_json, status, completed_tasks, created_at, updated_at
                ) VALUES (?, ?, 'created', 0, ?, ?)
                """,
                (manifest.run_id, manifest.model_dump_json(), now, now),
            )

    def update_run(self, run_id: str, status: str, completed_tasks: int) -> None:
        with self.connection:
            self.connection.execute(
                """
                UPDATE batch_runs
                SET status = ?, completed_tasks = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (status, completed_tasks, datetime.now(UTC).isoformat(), run_id),
            )

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM batch_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_runs(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.connection.execute(
                "SELECT * FROM batch_runs ORDER BY created_at DESC"
            ).fetchall()
        ]

    def replace_metrics(self, run_id: str, metrics: list[MetricRecord]) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM metric_records WHERE run_id = ?", (run_id,))
            self.connection.executemany(
                "INSERT INTO metric_records (run_id, metric_json) VALUES (?, ?)",
                [(run_id, metric.model_dump_json()) for metric in metrics],
            )

    def list_metrics(self, run_id: str) -> list[MetricRecord]:
        rows = self.connection.execute(
            "SELECT metric_json FROM metric_records WHERE run_id = ?", (run_id,)
        ).fetchall()
        return [MetricRecord.model_validate_json(row["metric_json"]) for row in rows]

    def save_manual_review(self, review: ManualReviewRecord) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO manual_reviews (output_id, review_json) VALUES (?, ?)",
                (review.output_id, review.model_dump_json()),
            )


def in_memory_repository() -> AnalysisRepository:
    repository = AnalysisRepository.__new__(AnalysisRepository)
    repository.database_path = Path(":memory:")
    repository.connection = sqlite3.connect(":memory:")
    repository.connection.row_factory = sqlite3.Row
    from src.storage.database import SCHEMA

    repository.connection.executescript(SCHEMA)
    repository.connection.commit()
    return repository
