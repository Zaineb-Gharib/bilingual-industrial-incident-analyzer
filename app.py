"""Bilingual Industrial Incident Analyzer entry page."""

import streamlit as st

from src.ui import configure_page, root_settings

configure_page("Bilingual Industrial Incident Analyzer")
st.title("Bilingual Industrial Incident Analyzer")
st.caption("双语工业事故分析器 · English / 中文 · Evidence-first structured analysis")

st.markdown(
    """
This portfolio system turns an English or Chinese technical incident report into a
strict, evidence-grounded JSON analysis. It compares zero-shot, few-shot, and
self-refinement prompting under one versioned contract.
"""
)

settings = root_settings()
if settings.provider == "demo":
    st.markdown(
        '<div class="demo-band">DEMO MODE is the safe default. It uses a deterministic rule engine, not an LLM, and must not be interpreted as model evaluation.</div>',
        unsafe_allow_html=True,
    )
elif settings.live_provider_ready:
    st.success("A live OpenAI-compatible provider is configured locally.")
else:
    st.warning(
        "The selected live provider is incomplete; check the local environment configuration."
    )

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("1 · Analyze")
    st.write(
        "Choose input/output languages, a prompting strategy, and inspect structured evidence."
    )
with c2:
    st.subheader("2 · Compare")
    st.write(
        "Run all strategies under the same provider/model settings and compare validity and latency."
    )
with c3:
    st.subheader("3 · Evaluate")
    st.write(
        "Use a frozen manifest, stable task IDs, resumable batches, and denominator-aware metrics."
    )

st.divider()
st.subheader("Safety and evidence policy")
st.write(
    "Recommendations are decision support only. Operational changes require authorized human review. "
    "Evidence quotes must be exact source substrings; unsupported or dangerous output is surfaced by validation."
)
st.info(
    "The bundled dataset contains synthetic, non-identifying incidents. Its 40 bilingual translations "
    "remain pending independent manual review and are not represented as human-approved."
)

with st.expander("Current safe configuration"):
    st.json(settings.safe_summary())
