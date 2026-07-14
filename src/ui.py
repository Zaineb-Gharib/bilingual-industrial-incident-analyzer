"""Shared Streamlit presentation helpers."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import streamlit as st

from src.config import Settings
from src.domain.enums import OutputLanguage, PromptingStrategy
from src.domain.models import AnalysisOutcome, AnalysisRequest
from src.providers.factory import available_provider_names
from src.services.factory import build_analysis_service

ROOT = Path(__file__).resolve().parents[1]


def configure_page(title: str) -> None:
    st.set_page_config(page_title=title, page_icon="🧩", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px;}
        .demo-band {background:#fff5d6;border:1px solid #edc967;border-radius:8px;
                    padding:.7rem 1rem;margin:.2rem 0 1rem;color:#5c4513;font-weight:600;}
        .small-note {color:#52606d;font-size:.88rem;}
        div[data-testid="stMetric"] {background:#f7f9fb;border:1px solid #d9e2ec;
                    border-radius:8px;padding:.65rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def root_settings(provider: str | None = None, model: str | None = None) -> Settings:
    settings = Settings.from_env(ROOT)
    return replace(
        settings,
        provider=provider or settings.provider,
        model=model or settings.model,
    )


def provider_controls(key: str) -> tuple[str, str, Settings]:
    settings = root_settings()
    providers = available_provider_names(settings)
    provider = st.selectbox(
        "Provider",
        providers,
        index=providers.index(settings.provider) if settings.provider in providers else 0,
        key=f"{key}_provider",
        help="The demo provider is a deterministic rule engine, not an LLM.",
    )
    default_model = "demo-v1" if provider == "demo" else settings.model
    model = st.text_input("Model", value=default_model, key=f"{key}_model")
    selected = root_settings(provider, model)
    if provider == "demo":
        st.markdown(
            '<div class="demo-band">DEMO MODE — deterministic rule engine; outputs and metrics are not LLM research results.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(
            "Live provider enabled from local environment configuration. The API key is never displayed."
        )
    return provider, model, selected


def analyze_once(
    text: str,
    output_language: str,
    strategy: str,
    provider: str,
    model: str,
    settings: Settings,
) -> AnalysisOutcome:
    service = build_analysis_service(settings, provider)
    return service.analyze(
        AnalysisRequest(
            incident_text=text,
            output_language=OutputLanguage(output_language),
            strategy=PromptingStrategy(strategy),
            provider_name=provider,
            model=model,
        )
    )


def render_outcome(outcome: AnalysisOutcome, heading: str | None = None) -> None:
    if heading:
        st.subheader(heading)
    status = outcome.validation.status.value
    if outcome.final_accepted_valid:
        st.success(f"Accepted: {status}")
    else:
        st.error(f"Not accepted: {status} · failure={outcome.failure_type.value}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Input detected", outcome.detected_input_language.value)
    c2.metric("Provider", outcome.provider)
    c3.metric("Semantic calls", outcome.semantic_call_count)
    c4.metric("Latency", f"{outcome.total_latency_ms:.1f} ms")
    if outcome.result:
        result = outcome.result
        st.markdown(f"### {result.incident_title}")
        a, b, c = st.columns(3)
        a.metric("Category", result.incident_category.value)
        b.metric("Severity", result.severity.value)
        c.metric("Responsible team", result.responsible_team.value)
        st.write(f"**Affected system:** {result.affected_system}")
        st.write("**Symptoms:** " + "; ".join(result.main_symptoms))
        st.write(
            f"**Suspected cause:** {result.suspected_cause.statement} "
            f"({result.suspected_cause.certainty.value})"
        )
        st.write("**Immediate actions**")
        for item in result.recommended_immediate_actions:
            st.write(f"- {item.action} — {item.rationale}")
        st.write("**Long-term actions**")
        for item in result.recommended_long_term_actions:
            st.write(f"- {item}")
        st.write("**Evidence**")
        for item in result.evidence:
            st.code(item.quote, language=None)
            st.caption("Supports: " + ", ".join(item.supports_fields))
        st.write(f"**Uncertainty:** {result.uncertainty_explanation}")
        st.write(f"**Confidence:** {result.confidence.level} — {result.confidence.explanation}")
        if result.warnings:
            st.warning("\n".join(result.warnings))
    if outcome.validation.issues:
        with st.expander(f"Validation details ({len(outcome.validation.issues)})", expanded=True):
            st.dataframe(
                [issue.model_dump(mode="json") for issue in outcome.validation.issues],
                width="stretch",
                hide_index=True,
            )
    with st.expander("Provenance and raw structured output"):
        st.json(
            {
                "analysis_id": outcome.analysis_id,
                "prompt_version": outcome.prompt_version,
                "prompt_hash": outcome.prompt_hash,
                "model": outcome.model,
                "first_pass_json_valid": outcome.first_pass_json_valid,
                "repair_assisted_valid": outcome.repair_assisted_valid,
                "final_accepted_valid": outcome.final_accepted_valid,
                "retry_count": outcome.retry_count,
            }
        )
        if outcome.initial_raw_response:
            st.write("Initial self-refinement response")
            st.code(outcome.initial_raw_response, language="json")
        if outcome.final_raw_response:
            st.write("Final response")
            st.code(outcome.final_raw_response, language="json")


def outcome_download(outcome: AnalysisOutcome, key: str) -> None:
    payload = outcome.model_dump(mode="json")
    st.download_button(
        "Download UTF-8 JSON",
        data=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"{outcome.analysis_id}.json",
        mime="application/json",
        key=key,
    )
