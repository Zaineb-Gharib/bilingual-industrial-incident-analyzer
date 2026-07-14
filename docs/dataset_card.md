# Dataset Card: BIIA-80 v1

## Summary

BIIA-80 v1 contains 40 synthetic English/Simplified-Chinese scenario pairs, or 80
language-specific incident reports. It is designed for a small, reproducible comparison of
prompting strategies, not for training or claims about industrial deployment.

## Composition

- Ten categories: server, network, database, deployment, API, storage, data pipeline,
  hardware, manufacturing equipment, and security.
- Four scenario pairs per category.
- Ten development pairs and thirty held-out evaluation pairs.
- Severity distribution: 3 critical, 16 high, 12 medium, and 9 low pairs.
- Every pair includes gold category/severity/team concepts, bilingual system and symptom
  concepts, conservative action concepts, cause certainty, exact evidence spans, ambiguity,
  safety notes, and creation provenance.

## Creation and review status

Codex generated the synthetic drafts from the versioned scenario matrix on 2026-07-14. No
real company, person, credential, IP address, or confidential event was used. The author is
recorded as `codex-ai-assisted-draft`; reviewer fields are empty. All 40 translations are
truthfully marked `pending_manual_review`.

No claim of native-speaker, domain-expert, or independent review is made.

## Split and leakage control

The scenario pair is the split unit; its translations cannot appear in different splits.
Only four development IDs are used in few-shot prompts. The validator checks IDs, split
counts, category balance, example provenance, and development/evaluation five-word-shingle
Jaccard overlap. v1 has no overlap flag at the configured 0.72 threshold. Lexical checks do
not replace human semantic leakage review.

## Files and encoding

- `incidents_v1.jsonl`: source of truth, UTF-8.
- `incidents_v1.csv`: generated inspection copy, UTF-8 with BOM.
- `scenario_matrix_v1.csv`: compact scenario design table.
- `dataset_manifest_v1.json`: counts, provenance, review status, and hash.

SHA-256 of source JSONL:
`49a2a982cda5aea08fb74dc4556d0ce9215346996a1911f14d5b96e5bc3a2312`.

## Appropriate uses

- Local schema, prompt, grounding, retry, batch, and dashboard development.
- Controlled, small-scale LLM prompting experiments after the live-cost gate.
- Portfolio demonstration with honest limitations.

## Inappropriate uses

- Autonomous operational decisions.
- Safety certification or production benchmarking.
- Training or evaluating systems for a named organization.
- Claims about broad industrial, cultural, or linguistic generalization.

## Required human work

Two bilingual reviewers should independently check meaning preservation, terminology,
severity, evidence spans, and action safety. Disagreements need adjudication and versioned
changes. A domain reviewer should separately assess operational labels and recommendations.

