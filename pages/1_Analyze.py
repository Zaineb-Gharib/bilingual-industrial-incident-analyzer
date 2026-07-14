"""Single incident analysis page."""

import streamlit as st

from src.domain.enums import OutputLanguage, PromptingStrategy
from src.evaluation.dataset_loader import load_dataset
from src.ui import (
    ROOT,
    analyze_once,
    configure_page,
    outcome_download,
    provider_controls,
    render_outcome,
)

configure_page("Analyze Incident")
st.title("Analyze one incident")
st.caption("Strict JSON · exact-substring evidence · explicit uncertainty")

records = load_dataset(ROOT / "data/incidents_v1.jsonl")
examples = {
    "English — database": next(
        record.source_en for record in records if record.category.value == "database_failure"
    ),
    "中文 — 部署": next(
        record.source_zh for record in records if record.category.value == "deployment_failure"
    ),
    "English — safety-critical equipment": next(
        record.source_en for record in records if record.severity.value == "critical"
    ),
}
example_name = st.selectbox("Example", list(examples), key="analyze_example")
if "incident_editor" not in st.session_state:
    st.session_state.incident_editor = examples[example_name]
if st.button("Load selected example"):
    st.session_state.incident_editor = examples[example_name]

text = st.text_area(
    "Incident report",
    key="incident_editor",
    height=190,
    max_chars=4000,
    help="10–4,000 characters. English, Chinese, or mixed text is accepted.",
)
c1, c2, c3 = st.columns(3)
with c1:
    output = st.selectbox("Output language", [item.value for item in OutputLanguage])
with c2:
    strategy = st.selectbox("Prompting strategy", [item.value for item in PromptingStrategy])
with c3:
    provider, model, settings = provider_controls("analyze")

if st.button("Analyze incident", type="primary", use_container_width=True):
    with st.spinner("Analyzing and validating…"):
        st.session_state.last_outcome = analyze_once(
            text, output, strategy, provider, model, settings
        )

if outcome := st.session_state.get("last_outcome"):
    render_outcome(outcome)
    outcome_download(outcome, "single_download")
