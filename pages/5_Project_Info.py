"""Portfolio documentation and limitations page."""

import streamlit as st

from src.evaluation.dataset_loader import dataset_sha256, load_dataset, validate_dataset
from src.ui import ROOT, configure_page, root_settings

configure_page("Project Information")
st.title("Project information")
st.caption("Architecture, reproducibility, dataset governance, and honest limitations")

records = load_dataset(ROOT / "data/incidents_v1.jsonl")
summary = validate_dataset(records)
settings = root_settings()

st.subheader("System boundaries")
st.write(
    "The provider-neutral orchestration layer builds versioned prompts, invokes a configured adapter, "
    "parses strict JSON, validates schema/grounding/language/safety, and stores append-oriented run records."
)

st.subheader("The three prompt strategies, in plain language")
st.write(
    "**Zero-shot** gives the model the task and schema but no worked example. "
    "**Few-shot** adds a small set of development-only examples. "
    "**Self-refinement** asks for an initial answer, reviews its validation weaknesses, then permits one "
    "corrected answer. It is intentionally limited to one cycle."
)
st.code(
    "Input → prompt strategy → provider adapter → strict parser → schema + evidence + safety validators → SQLite/results",
    language=None,
)

c1, c2, c3 = st.columns(3)
c1.metric("Bilingual pairs", summary["scenario_pairs"])
c2.metric("Evaluation pairs", summary["split_counts"]["evaluation"])
c3.metric("Pending translation reviews", summary["pending_manual_review"])
st.caption(f"Dataset SHA-256: {dataset_sha256(settings.dataset_path)}")

st.subheader("Claims this project does not make")
st.write(
    "The synthetic dataset is AI-assisted and has not yet received independent translation approval. "
    "Demo-provider outputs are not LLM results. Automatic exact-match metrics are not substitutes for "
    "expert factuality or safety review. The analyzer is not an autonomous incident-response system."
)

st.subheader("Privacy, safety, and ethics")
st.write(
    "Raw user text is not stored by default, credentials are environment-only, and logs redact key-like "
    "values. Recommendations require an authorized person. The application blocks known dangerous action "
    "patterns and treats source text as untrusted data, but deterministic checks cannot guarantee safety."
)

st.subheader("Reproduce locally")
st.code(
    "python -m venv .venv\n"
    "source .venv/bin/activate\n"
    "pip install -r requirements.txt\n"
    "python scripts/validate_dataset.py\n"
    "pytest\n"
    "streamlit run app.py",
    language="bash",
)

st.subheader("Documentation")
st.write(
    "See README.md for the interview walkthrough and docs/ for the specification, architecture, "
    "evaluation protocol, dataset card, provider configuration, and review rubric."
)
