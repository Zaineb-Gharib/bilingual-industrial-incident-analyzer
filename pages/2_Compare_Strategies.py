"""Prompt strategy comparison page."""

import streamlit as st

from src.domain.enums import OutputLanguage, PromptingStrategy
from src.domain.models import AnalysisRequest
from src.evaluation.dataset_loader import load_dataset
from src.evaluation.metrics import required_field_completion
from src.services.comparison_service import ComparisonService
from src.services.factory import build_analysis_service
from src.ui import ROOT, configure_page, provider_controls, render_outcome

configure_page("Compare Strategies")
st.title("Compare prompting strategies")
st.caption("Same report, provider, model, temperature, schema, and output language")

records = load_dataset(ROOT / "data/incidents_v1.jsonl")
default_text = records[6].source_en
text = st.text_area("Incident report", default_text, height=170, max_chars=4000)
c1, c2 = st.columns(2)
with c1:
    output = st.selectbox("Output language", [item.value for item in OutputLanguage])
with c2:
    provider, model, settings = provider_controls("compare")

if st.button("Run fair comparison", type="primary", use_container_width=True):
    service = build_analysis_service(settings, provider)
    comparison = ComparisonService(service)
    with st.spinner("Running three strategies…"):
        st.session_state.comparison = comparison.compare(
            AnalysisRequest(
                incident_text=text,
                output_language=OutputLanguage(output),
                strategy=PromptingStrategy.ZERO_SHOT,
                provider_name=provider,
                model=model,
            )
        )

if comparison := st.session_state.get("comparison"):
    summary = []
    for strategy, outcome in comparison.items():
        parsed = outcome.result.model_dump(mode="json") if outcome.result else None
        grounded = outcome.validation.grounded_evidence_items
        returned = outcome.validation.returned_evidence_items
        summary.append(
            {
                "strategy": strategy.value,
                "accepted": outcome.final_accepted_valid,
                "status": outcome.validation.status.value,
                "semantic_calls": outcome.semantic_call_count,
                "retries": outcome.retry_count,
                "latency_ms": round(outcome.total_latency_ms, 2),
                "repair_used": outcome.repair_assisted_valid,
                "completeness": required_field_completion(parsed),
                "evidence_grounding": grounded / returned if returned else None,
                "warnings": len(outcome.validation.issues),
            }
        )
    st.subheader("Controlled comparison")
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.caption(
        "A difference on one report does not establish universal superiority; use a frozen dataset and "
        "the evaluation protocol for broader claims."
    )
    tabs = st.tabs([item.value for item in PromptingStrategy])
    for tab, strategy in zip(tabs, PromptingStrategy, strict=True):
        with tab:
            render_outcome(comparison[strategy])
