"""Create stable, balanced language-path tasks from paired records."""

from __future__ import annotations

from collections.abc import Iterable

from src.domain.enums import DatasetSplit, OutputLanguage, PromptingStrategy
from src.schemas.dataset import DatasetScenarioPair
from src.schemas.run_records import EvaluationTask
from src.utils.ids import stable_id


def build_evaluation_tasks(
    records: Iterable[DatasetScenarioPair],
    split: DatasetSplit = DatasetSplit.EVALUATION,
    strategies: Iterable[PromptingStrategy] = tuple(PromptingStrategy),
) -> list[EvaluationTask]:
    selected = sorted(
        (record for record in records if record.split == split),
        key=lambda record: record.scenario_id,
    )
    tasks: list[EvaluationTask] = []
    for pair_index, record in enumerate(selected):
        output_language = OutputLanguage.EN if pair_index % 2 == 0 else OutputLanguage.ZH
        for source_language, source in [("en", record.source_en), ("zh", record.source_zh)]:
            for strategy in strategies:
                task_id = stable_id(
                    "task",
                    record.dataset_version,
                    record.scenario_id,
                    source_language,
                    output_language.value,
                    strategy.value,
                )
                tasks.append(
                    EvaluationTask(
                        task_id=task_id,
                        scenario_id=record.scenario_id,
                        dataset_version=record.dataset_version,
                        split=record.split.value,
                        source_language=source_language,
                        output_language=output_language,
                        strategy=strategy,
                        incident_text=source,
                    )
                )
    return rotate_strategy_order(tasks)


def rotate_strategy_order(tasks: list[EvaluationTask]) -> list[EvaluationTask]:
    grouped: dict[tuple[str, str, str], list[EvaluationTask]] = {}
    for task in tasks:
        key = (task.scenario_id, task.source_language, task.output_language.value)
        grouped.setdefault(key, []).append(task)
    ordered: list[EvaluationTask] = []
    for index, key in enumerate(sorted(grouped)):
        group = sorted(grouped[key], key=lambda task: task.strategy.value)
        shift = index % len(group)
        ordered.extend(group[shift:] + group[:shift])
    return ordered
