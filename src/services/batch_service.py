"""Frozen-manifest, resumable batch evaluation."""

from __future__ import annotations

from collections.abc import Callable

from src.config import Settings
from src.domain.enums import DatasetSplit
from src.domain.models import AnalysisOutcome, AnalysisRequest
from src.evaluation.dataset_loader import dataset_sha256
from src.evaluation.metrics import aggregate_all_groups
from src.evaluation.task_builder import build_evaluation_tasks
from src.schemas.dataset import DatasetScenarioPair
from src.schemas.run_records import EvaluationTask, RunManifest
from src.services.analysis_service import AnalysisService
from src.storage.repositories import AnalysisRepository
from src.utils.ids import random_id


def estimated_semantic_calls(tasks: list[EvaluationTask]) -> int:
    return sum(2 if task.strategy.value == "self_refinement" else 1 for task in tasks)


class BatchService:
    def __init__(
        self,
        settings: Settings,
        analysis_service: AnalysisService,
        repository: AnalysisRepository,
    ):
        self.settings = settings
        self.analysis_service = analysis_service
        self.repository = repository

    def prepare(
        self,
        records: list[DatasetScenarioPair],
        split: DatasetSplit,
        notes: str = "",
        language_paths: set[str] | None = None,
    ) -> tuple[RunManifest, list[EvaluationTask]]:
        tasks = build_evaluation_tasks(records, split)
        if language_paths:
            tasks = [
                task
                for task in tasks
                if f"{task.source_language}->{task.output_language.value}" in language_paths
            ]
        if not tasks:
            raise ValueError("The selected split and language paths produced no tasks.")
        manifest = RunManifest(
            run_id=random_id("run"),
            dataset_version="1.0",
            dataset_hash=dataset_sha256(self.settings.dataset_path),
            prompt_version="1.0",
            schema_version="1.0",
            provider=self.analysis_service.provider.name,
            model=self.settings.model,
            temperature=self.settings.temperature,
            timeout_seconds=self.settings.timeout_seconds,
            transport_retries=self.settings.max_retries,
            syntax_repair_enabled=True,
            task_ids=[task.task_id for task in tasks],
            notes=notes,
        )
        self.repository.create_run(manifest)
        return manifest, tasks

    def run(
        self,
        manifest: RunManifest,
        tasks: list[EvaluationTask],
        records: list[DatasetScenarioPair],
        live_batch_approved: bool = False,
        progress: Callable[[int, int, AnalysisOutcome], None] | None = None,
        cancel_requested: Callable[[], bool] | None = None,
        max_new_tasks: int | None = None,
    ) -> list[AnalysisOutcome]:
        if manifest.provider != "demo" and not live_batch_approved:
            raise PermissionError("A live batch requires explicit approval after cost review.")
        if [task.task_id for task in tasks] != manifest.task_ids:
            raise ValueError("Task list does not match the frozen run manifest.")
        completed = self.repository.completed_task_ids(manifest.run_id)
        pending = [task for task in tasks if task.task_id not in completed]
        if max_new_tasks is not None:
            pending = pending[:max_new_tasks]
        outcomes: list[AnalysisOutcome] = []
        self.repository.update_run(manifest.run_id, "running", len(completed))
        total = len(tasks)
        for task in pending:
            if cancel_requested and cancel_requested():
                self.repository.update_run(
                    manifest.run_id,
                    "stopped",
                    len(self.repository.completed_task_ids(manifest.run_id)),
                )
                break
            outcome = self.analysis_service.analyze(
                AnalysisRequest(
                    incident_text=task.incident_text,
                    output_language=task.output_language,
                    strategy=task.strategy,
                    provider_name=manifest.provider,
                    model=manifest.model,
                    run_id=manifest.run_id,
                    task_id=task.task_id,
                    dataset_version=task.dataset_version,
                    scenario_id=task.scenario_id,
                    store_raw_override=True,
                )
            )
            outcomes.append(outcome)
            done = len(self.repository.completed_task_ids(manifest.run_id))
            self.repository.update_run(manifest.run_id, "running", done)
            if progress:
                progress(done, total, outcome)
        done = len(self.repository.completed_task_ids(manifest.run_id))
        if done == total:
            self.repository.update_run(manifest.run_id, "completed", done)
            rows = self.repository.list_analyses(manifest.run_id)
            self.repository.replace_metrics(
                manifest.run_id,
                aggregate_all_groups(manifest.run_id, rows, records),
            )
        return outcomes
