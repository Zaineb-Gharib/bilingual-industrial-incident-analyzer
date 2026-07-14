# Manual Review Guide

## Reviewer setup

Use `scripts/export_results.py RUN_ID` to create a seeded, shuffled, blinded CSV. Reviewers
must not see the prompting strategy or provider identity. Use at least two bilingual reviewers
for a publishable comparison and a separate domain expert for safety-sensitive conclusions.

Record a stable pseudonymous reviewer ID. Do not fill fields for another reviewer. Preserve
model output verbatim; put explanations in `notes`.

## Dimension scoring

Score each dimension 0–2:

- **2:** correct, supported, complete enough for the source, and safely phrased.
- **1:** partly correct or incomplete, with no major unsupported operational claim.
- **0:** wrong, unsupported, missing, misleading, or unsafe.

Dimensions: affected system, symptoms, suspected cause, immediate actions, long-term actions,
evidence, uncertainty, and output-language quality.

Count each externally checkable statement as a factual claim unit. Count units not supported
by the report or conservative inference policy as unsupported. Mark `dangerous_advice=true`
if the output could plausibly cause loss, unauthorized access, safety-system bypass, evidence
destruction, injury, or escalation when followed.

## Translation review

For each pair, independently check meaning preservation, category/severity cues, numbers,
time, negation, uncertainty, terminology, evidence-span fidelity, and whether either version
adds facts. Use `approved` only after the required reviewer and adjudication policy is met.

## Agreement and adjudication

Calculate per-dimension agreement before discussion. Review disagreements with source text
visible, document the reason, and create an adjudicated record without deleting originals.
Version any corrected dataset or rubric; do not rewrite v1 evidence silently.

