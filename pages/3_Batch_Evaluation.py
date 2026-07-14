"""Frozen-manifest, resumable evaluation controls."""

import json

import pandas as pd
import streamlit as st

from src.domain.enums import DatasetSplit
from src.evaluation.dataset_loader import load_dataset, load_few_shot_ids, validate_dataset
from src.services.batch_service import BatchService, estimated_semantic_calls
from src.services.factory import build_analysis_service
from src.ui import ROOT, configure_page, provider_controls

configure_page("Batch Evaluation")
st.title("Batch evaluation")
st.caption("Frozen manifest · stable task IDs · resumable execution · explicit live-cost approval")

records = load_dataset(ROOT / "data/incidents_v1.jsonl")
few_shot_ids = load_few_shot_ids(ROOT / "prompts/examples_v1.json")
validation = validate_dataset(records, few_shot_ids)
st.success(
    f"Dataset valid: {validation['scenario_pairs']} bilingual pairs; "
    f"{validation['pending_manual_review']} translations pending manual review."
)

c1, c2 = st.columns(2)
with c1:
    split_value = st.selectbox("Split", [item.value for item in DatasetSplit])
    language_paths = st.multiselect(
        "Language paths",
        ["en->en", "en->zh", "zh->en", "zh->zh"],
        default=["en->en", "en->zh", "zh->en", "zh->zh"],
    )
    task_limit = st.number_input(
        "Safe checkpoint size (0 = run all pending outputs)",
        min_value=0,
        max_value=180,
        value=0,
        help="Choose a small number to stop cleanly after that many outputs; rerun to resume.",
    )
with c2:
    provider, model, settings = provider_controls("batch")

service = build_analysis_service(settings, provider)
batch = BatchService(settings, service, service.repository)
split = DatasetSplit(split_value)

if st.button("Prepare frozen run manifest", width="stretch"):
    manifest, tasks = batch.prepare(
        records,
        split,
        notes="Prepared in Streamlit UI; paths=" + ",".join(language_paths),
        language_paths=set(language_paths),
    )
    st.session_state.batch_manifest = manifest
    st.session_state.batch_tasks = tasks

manifest = st.session_state.get("batch_manifest")
tasks = st.session_state.get("batch_tasks")
if manifest and tasks:
    st.subheader("Prepared run")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Outputs", len(tasks))
    m2.metric("Base semantic calls", estimated_semantic_calls(tasks))
    m3.metric("Provider", manifest.provider)
    m4.metric("Split", split_value)
    st.caption("Retries and optional syntax-repair calls can increase the actual total.")
    with st.expander("Frozen manifest"):
        st.json(manifest.model_dump(mode="json"))

    live_approved = False
    if manifest.provider != "demo":
        st.error(
            "LIVE PAID BATCH: review provider pricing and the call estimate. "
            "The application cannot guarantee cost from request count alone."
        )
        phrase = st.text_input("Type APPROVE LIVE BATCH to authorize this run")
        live_approved = phrase == "APPROVE LIVE BATCH"

    if st.button(
        "Run / resume prepared batch",
        type="primary",
        disabled=manifest.provider != "demo" and not live_approved,
        width="stretch",
    ):
        progress = st.progress(0.0, text="Starting…")

        def update(done: int, total: int, _outcome: object) -> None:
            progress.progress(done / total, text=f"Completed {done}/{total}")

        outcomes = batch.run(
            manifest,
            tasks,
            records,
            live_batch_approved=live_approved,
            progress=update,
            max_new_tasks=int(task_limit) or None,
        )
        completed = len(service.repository.completed_task_ids(manifest.run_id))
        st.success(f"Processed {len(outcomes)} new outputs; {completed}/{len(tasks)} complete.")
        if completed == len(tasks):
            st.info("Automatic metrics have been persisted. Open the Evaluation Dashboard.")

    completed_rows = service.repository.list_analyses(manifest.run_id)
    if completed_rows:
        st.subheader("Current run artifacts")
        csv_bytes = pd.DataFrame(completed_rows).to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Download record-level CSV",
            data=csv_bytes,
            file_name=f"{manifest.run_id}_analyses.csv",
            mime="text/csv",
        )
        metrics = service.repository.list_metrics(manifest.run_id)
        if metrics:
            st.download_button(
                "Download metrics JSON",
                data=json.dumps(
                    [item.model_dump(mode="json") for item in metrics],
                    ensure_ascii=False,
                    indent=2,
                ).encode("utf-8"),
                file_name=f"{manifest.run_id}_metrics.json",
                mime="application/json",
            )
