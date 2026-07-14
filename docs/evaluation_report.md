# Evaluation Report

## Current status

The deterministic development and evaluation runs exercise the full pipeline locally. They
are labeled **demo-provider metrics** and are not LLM performance results. No real provider
call or full paid evaluation has been executed because no approved credential/cost gate has
been completed in this build session.

Human factuality, translation, and safety scores are pending. The project therefore does not
claim that any prompt strategy is empirically superior.

## Executed held-out demo run

- Run ID: `run-7343b258a9b64a77bc4716bd15d07445`.
- Source commit at execution: `f88dbfc`.
- Provider/model: deterministic `demo` / `demo-v1`; **not an LLM**.
- Scope: 180/180 held-out outputs, 240 base semantic calls, 0 transport retries, 0 JSON
  repairs, 0 terminal failures.
- Dataset hash:
  `49a2a982cda5aea08fb74dc4556d0ce9215346996a1911f14d5b96e5bc3a2312`.
- Category success: 129/180 (0.7167).
- Severity success: 75/180 (0.4167).
- Responsible-team exact match: 129/180 (0.7167).
- First-pass and final accepted validity: 180/180 (1.0000).
- Evidence grounding: 180/180 quotes (1.0000); hallucinated quotes: 0/180.
- Symptom precision/recall/F1: 0.0000 because generic demo symptoms do not match the
  versioned gold concepts.
- Bilingual consistency: weighted sum 75.0 / 90 matched pairs = 0.8333.
- Mean/median/p95 local latency: 1.444 / 1.154 / 2.583 ms.

Latency is local rule-engine time and is not comparable with network inference. The exported
manual-review sheet is deliberately unscored. Strategy breakdowns are mechanically similar
because all three routes ultimately use the same deterministic rules; this run cannot answer
the LLM research question.

During the later browser verification pass, the demo evidence segmenter exposed a decimal
boundary defect: a source sentence containing `2.8` could be shortened to `2.`. Commit
`ce4a0ac` fixes that parser and adds a regression test. The recorded aggregate run above is
preserved as an immutable historical artifact from `f88dbfc`; its aggregate metrics are not
silently recomputed. This also illustrates an important limitation: the automatic grounding
metric checks whether a quote is an exact source substring, not whether the quote is
informative enough to support the analysis.

## Frozen design

- Dataset version 1.0 and schema/prompt version 1.0.
- Held-out evaluation: 30 pairs, 60 source reports, three strategies, 180 outputs.
- Target language alternates by scenario pair to balance all four language paths.
- Zero/few-shot use one base call; self-refinement uses two: 240 base semantic calls.
- Task order rotates strategy position to reduce simple ordering bias.
- Stable task IDs permit resuming without duplicating completed outputs.

## Automatic metrics

Each record includes a numerator, denominator, exclusion count, source, version, and group.

- Category/severity conditional accuracy: correct among parsed outputs.
- Category/severity end-to-end success: correct divided by every attempted output.
- Responsible-team exact match.
- Symptom concept precision, recall, and F1.
- First-pass JSON validity, final/repair-assisted validity, and outputs requiring repair.
- Required-field completion.
- Grounded evidence quotes divided by returned quotes.
- Hallucinated evidence quotes divided by returned quotes.
- Outputs with at least one grounded quote.
- Bilingual consistency: weighted agreement in category, severity, team, system, and symptom
  fields where both source-language versions yield accepted outputs.
- Failure rate and average/median/p95 latency.

Breakdowns are stored overall, by strategy, input/output language, language path, and category.

## Manual metrics

The blinded rubric separately scores affected system, symptoms, cause, immediate actions,
long-term actions, evidence, uncertainty, output-language quality, unsupported factual claim
units, and dangerous advice. Empty reviewer fields mean unreviewed; they must never be
coerced to zero.

## Interpretation cautions

High demo results reflect deterministic rules and dataset wording. Exact match can penalize a
valid paraphrase. Bilingual agreement does not prove correctness. Evidence presence does not
prove the evidence supports the claim. Small per-category denominators create noisy estimates.

## Live experiment pending gate

Configure a provider, run two small synthetic checks, estimate token/cost ranges from actual
usage and current pricing, and obtain explicit approval before running 240+ live calls. Append
the manifest, failure counts, automatic metrics, manual-review coverage, and limitations here
only after they are actually measured.
