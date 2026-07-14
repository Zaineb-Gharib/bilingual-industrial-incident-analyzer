"""SQLite connection and schema initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS analysis_records (
    analysis_id TEXT PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    run_id TEXT,
    task_id TEXT,
    dataset_version TEXT,
    scenario_id TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    strategy TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    input_language TEXT NOT NULL,
    output_language TEXT NOT NULL,
    created_at TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    retry_count INTEGER NOT NULL,
    semantic_call_count INTEGER NOT NULL,
    validation_status TEXT NOT NULL,
    failure_type TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    raw_input TEXT,
    initial_raw_response TEXT,
    final_raw_response TEXT,
    repair_raw_response TEXT,
    parsed_response TEXT,
    validation_issues TEXT NOT NULL,
    first_pass_json_valid INTEGER NOT NULL,
    repair_assisted_valid INTEGER NOT NULL,
    final_accepted_valid INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_analysis_run ON analysis_records(run_id);
CREATE INDEX IF NOT EXISTS idx_analysis_task ON analysis_records(task_id);

CREATE TABLE IF NOT EXISTS attempt_records (
    attempt_id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    transport_attempt INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    raw_response TEXT,
    error_type TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS batch_runs (
    run_id TEXT PRIMARY KEY,
    manifest_json TEXT NOT NULL,
    status TEXT NOT NULL,
    completed_tasks INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metric_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    metric_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS manual_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id TEXT NOT NULL,
    review_json TEXT NOT NULL
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    connection.commit()
    return connection
