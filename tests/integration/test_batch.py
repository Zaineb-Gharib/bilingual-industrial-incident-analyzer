from src.domain.enums import DatasetSplit
from src.evaluation.dataset_loader import load_dataset
from src.services.batch_service import BatchService, estimated_semantic_calls
from src.services.factory import build_analysis_service


def test_development_batch_completes_and_persists_metrics(settings) -> None:
    records = load_dataset(settings.dataset_path)
    service = build_analysis_service(settings, "demo")
    batch = BatchService(settings, service, service.repository)
    manifest, tasks = batch.prepare(records, DatasetSplit.DEVELOPMENT, notes="integration test")
    assert len(tasks) == 60
    assert estimated_semantic_calls(tasks) == 80
    outcomes = batch.run(manifest, tasks, records)
    assert len(outcomes) == 60
    assert service.repository.get_run(manifest.run_id)["status"] == "completed"
    metrics = service.repository.list_metrics(manifest.run_id)
    assert metrics
    assert any(item.metric_name == "evidence_grounding_rate" for item in metrics)


def test_live_batch_requires_explicit_approval(settings) -> None:
    records = load_dataset(settings.dataset_path)
    service = build_analysis_service(settings, "demo")
    batch = BatchService(settings, service, service.repository)
    manifest, tasks = batch.prepare(records, DatasetSplit.DEVELOPMENT)
    live_manifest = manifest.model_copy(update={"provider": "openai_compatible"})
    try:
        batch.run(live_manifest, tasks, records)
    except PermissionError:
        pass
    else:
        raise AssertionError("live run was not gated")


def test_batch_resumes_without_duplicate_tasks(settings) -> None:
    records = load_dataset(settings.dataset_path)
    service = build_analysis_service(settings, "demo")
    batch = BatchService(settings, service, service.repository)
    manifest, tasks = batch.prepare(
        records, DatasetSplit.DEVELOPMENT, language_paths={"en->en", "en->zh"}
    )
    first = batch.run(manifest, tasks, records, max_new_tasks=3)
    assert len(first) == 3
    assert len(service.repository.completed_task_ids(manifest.run_id)) == 3
    second = batch.run(manifest, tasks, records, max_new_tasks=2)
    assert len(second) == 2
    assert len(service.repository.completed_task_ids(manifest.run_id)) == 5
    assert len({row["task_id"] for row in service.repository.list_analyses(manifest.run_id)}) == 5


def test_chinese_survives_sqlite_round_trip(settings) -> None:
    records = load_dataset(settings.dataset_path)
    service = build_analysis_service(settings, "demo")
    batch = BatchService(settings, service, service.repository)
    manifest, tasks = batch.prepare(records, DatasetSplit.DEVELOPMENT, language_paths={"zh->zh"})
    batch.run(manifest, tasks, records, max_new_tasks=1)
    row = service.repository.list_analyses(manifest.run_id)[0]
    assert row["raw_input"] == tasks[0].incident_text
    assert any("\u4e00" <= character <= "\u9fff" for character in row["raw_input"])
