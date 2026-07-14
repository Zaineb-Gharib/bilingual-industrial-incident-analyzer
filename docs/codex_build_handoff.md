# Codex Build Handoff

**Audience:** The future coding agent implementing the Bilingual Industrial Incident Analyzer  
**Current state:** Specification complete; application not implemented  
**Primary rule:** Build only what is specified for version 1, verify each phase, and do not invent results.

---

# 1. Mission

Implement a beginner-readable Python/Streamlit portfolio application that:

- accepts short English or Simplified Chinese technical/industrial incident reports;
- lets the user request English or Chinese output;
- returns strict, validated, evidence-grounded JSON;
- supports zero-shot, few-shot, and exactly one-cycle self-refinement;
- compares prompting strategies without fine-tuning;
- evaluates on a versioned 40-pair/80-report synthetic dataset;
- records failures, metadata, and reproducibility information;
- remains provider-neutral;
- never acts as an autonomous incident-response authority.

The implementation target is 7-14 focused days. Prefer a complete, tested, understandable version 1 over advanced optional features.

## Explanation in Simple Words

Build a small reliable research prototype. Do not expand it into a production operations platform.

---

# 2. Required Reading Order

Read completely before editing:

1. project_specification.md - authoritative behavior and architecture.
2. implementation_checklist.md - ordered work and definitions of done.
3. dataset_design.md - data construction and leakage rules.
4. evaluation_plan.md - formulas and fair comparison.
5. ui_wireframes.md - UI states and warnings.
6. github_publication_plan.md - release and safety gates.

If documents conflict:

1. privacy/safety rules win;
2. project_specification.md is the main product contract;
3. the focused document is authoritative for its domain;
4. record any necessary change in an architecture decision note and update affected docs.

## Explanation in Simple Words

The documents are connected. Reading them in order prevents a coding decision from accidentally breaking the dataset or experiment.

---

# 3. Do Not Do These Things

- Do not publish to GitHub until explicitly authorized in a later phase.
- Do not create fake results, badges, screenshots, charts, or test claims.
- Do not make live API calls in default tests.
- Do not commit a key, .env, local DB, or private input.
- Do not place provider calls directly in Streamlit pages.
- Do not put evaluation examples in the few-shot prompt.
- Do not let self-refinement loop.
- Do not silently turn repaired JSON into first-pass validity.
- Do not translate evidence quotes.
- Do not execute recommended actions or give destructive/physical repair commands.
- Do not use an LLM judge as unquestionable ground truth.
- Do not expand version 1 into RAG, multi-agent operations, authentication, or cloud infrastructure unless the user changes scope.

## Explanation in Simple Words

These restrictions protect the project’s honesty, budget, privacy, and manageable scope.

---

# 4. Architecture Contract

Use these dependency boundaries:

~~~text
Streamlit pages
    ↓
Application services
    ↓
Prompt manager + Provider protocol + Validation + Repositories
    ↓
Provider adapter / SQLite adapter

Batch evaluation → the same AnalysisService → metrics/reporting
~~~

Rules:

- pages display and collect data only;
- services own workflows and retry/refinement policy;
- prompt manager owns trusted templates and user-data separation;
- provider base owns neutral request/response/error types;
- vendor SDK imports exist only in its adapter;
- validators return structured issues;
- repositories append immutable attempt records;
- metrics are pure functions over exported records/gold;
- logging observes sanitized IDs/metadata and never stores keys.

## Explanation in Simple Words

The screen should not know how one vendor’s API works. A service coordinates the work, and small modules perform one job each.

---

# 5. Version 1 Decisions Already Made

Implement these unless a documented blocking constraint appears:

- Python 3.11+.
- Pydantic v2.
- Streamlit single frontend.
- SQLite local primary results store.
- JSONL canonical dataset; CSV generated for inspection/export.
- Simplified Chinese.
- 10 main categories plus other and unknown.
- Severity critical/high/medium/low/unknown.
- Report input 10-4,000 Unicode characters after trim.
- Evidence remains exact source-language substrings.
- Extra output fields forbidden.
- One reference provider plus deterministic fake.
- Self-refinement uses two semantic calls total: initial plus one combined review-and-correct.
- Transport retry maximum two after the initial attempt.
- Optional syntax-only repair maximum one and reported separately.
- 40 paired scenarios: 10 development, 30 evaluation.
- Core evaluation: 60 balanced tasks, 180 primary strategy outputs, 240 planned base semantic calls.
- Default tests: zero network calls.

## Explanation in Simple Words

These choices are fixed to keep the build moving. Changing them can affect code, prompts, data, and evaluation, so changes need a written reason.

---

# 6. Decisions You Must Make Before Live Evaluation

Create docs/decisions/ and record:

## ADR-001 Reference Provider and Model

Choose based on current availability, cost, privacy terms, Chinese capability, structured output, and SDK stability. Record exact provider/model/date. Do not assume the model listed in an old plan is current.

## ADR-002 Structured Output Mode

Choose provider-native JSON schema mode or prompt-only JSON. Apply the same mode to all strategies in the primary run. Local Pydantic validation remains required.

## ADR-003 Few-Shot Example IDs

Select four development IDs covering both inputs/outputs and unknown/explicit cause. Freeze them with prompt v1.

## ADR-004 Raw Input Storage Default

Recommended: store raw synthetic dataset inputs; do not store raw ad hoc inputs unless the user opts in locally.

## ADR-005 Bilingual Review

Record whether a second reviewer is available and what subset they review.

## ADR-006 Optional Evaluation Features

Decide whether repeats, bootstrap intervals, embeddings, or an LLM judge fit the budget. They must not delay the core evaluation.

## ADR-007 License

Choose code/data licenses after dependency and provenance review.

## Explanation in Simple Words

These choices depend on future access, budget, and people. Write them down before the real experiment so the rules do not change halfway through.

---

# 7. Build Order

Follow implementation_checklist.md. Critical dependency chain:

~~~text
Setup
 → schema/domain
 → fake provider
 → prompt manager
 → strict validation
 → single analysis + storage
 → one-cycle self-refinement
 → paired dataset + validation/freeze
 → batch runner + manifest/resume
 → metrics + manual review
 → comparison/dashboard
 → full offline tests
 → frozen real evaluation
 → truthful documentation/screenshots
 → publication review
~~~

Dataset drafting can overlap provider/prompt work, but:

- gold labels must be created before model answers influence them;
- evaluation records must not enter prompt development;
- primary run waits for all freezes and test gates.

## Explanation in Simple Words

Foundations come first. A pretty dashboard is not useful until outputs, failures, and metric calculations are trustworthy.

---

# 8. Required Core Types

At minimum define:

- InputLanguage, OutputLanguage, IncidentCategory, Severity, Certainty, ResponsibleTeam;
- IncidentAnalysis and nested schema models;
- AnalysisRequest;
- PromptPackage;
- LLMRequest and LLMResponse;
- ProviderError hierarchy;
- ValidationIssue and ValidationOutcome;
- AttemptRecord and AnalysisOutcome;
- DatasetScenarioPair;
- EvaluationTask and RunManifest;
- MetricRecord and ManualReviewRecord.

IDs:

- run_id: one batch/configuration.
- task_id: stable dataset/source/output/strategy identity.
- analysis_id: one logical analysis.
- attempt_id: one transport call.
- parent_attempt_id or stage link: initial/refined/repair relation.
- correlation_id: safe trace across logs.

Do not use a single opaque result dictionary throughout the application.

## Explanation in Simple Words

Named types are structured containers. They help the coding agent and tests know what data is allowed at each step.

---

# 9. Analysis Service State Machine

Recommended states:

~~~text
RECEIVED
 → INPUT_VALIDATED
 → PROMPT_RENDERED
 → PROVIDER_ATTEMPTED
 → RAW_SAVED
 → PARSED
 → VALIDATED
 → [REFINEMENT_REQUESTED → REFINED_RAW_SAVED → REFINED_VALIDATED]
 → [SYNTAX_REPAIR_REQUESTED → REPAIR_RAW_SAVED → REPAIR_VALIDATED]
 → COMPLETED | FAILED
~~~

Rules:

- Save raw response before parsing.
- Transport retry repeats the same stage and does not count as semantic refinement.
- Self-refinement stage can happen once.
- Syntax repair is optional, once, and never changes primary status.
- A failed refinement is not silently replaced with the initial output.
- Return a safe user outcome even if technical persistence/logging captures more detail.

## Explanation in Simple Words

A state machine is a list of allowed steps. It makes retry and refinement behavior easier to understand and prevents accidental infinite loops.

---

# 10. Prompt Implementation Notes

- Transcribe templates from project_specification.md Section 8.
- Use separate system and user messages.
- Keep incident text in the user data block.
- Serialize template inputs safely; report braces must not break formatting.
- Insert a schema generated from Pydantic or a tested stable compact representation.
- Record prompt template hash, language module, and example IDs.
- Freeze prompt v1 before primary evaluation.
- If a prompt changes behavior, create v2 rather than editing history.

Recommended self-refinement implementation:

1. Initial prompt returns complete JSON.
2. Validate.
3. Second prompt receives report, raw/canonical initial answer, and safe validator warnings.
4. Second prompt both reviews and returns one complete corrected JSON.
5. Validate and stop.

Do not implement separate review and third final-answer calls in v1.

## Explanation in Simple Words

The prompt text is part of the experiment, so it is versioned like code. The report is treated as untrusted input, not as an instruction.

---

# 11. Provider Implementation Notes

Neutral response should contain:

- raw text;
- provider and requested/resolved model;
- finish reason;
- provider request ID if safe;
- prompt/completion/total token usage if available;
- started/finished UTC timestamps;
- monotonic latency;
- structured-output mode;
- safe capability metadata.

Translate vendor exceptions:

- ProviderAuthenticationError;
- ProviderRateLimitError with retry_after;
- ProviderTimeoutError;
- ProviderTransientError;
- ProviderBadRequestError;
- ProviderUnsupportedResponseError.

The service, not the adapter, owns cross-provider retry policy. The adapter may configure SDK internal retries to zero or account for them explicitly so attempts are not hidden.

## Explanation in Simple Words

The adapter translates one vendor’s language into the project’s common language. This prevents the rest of the program from depending on one API.

---

# 12. Validation Acceptance Rules

A primary output is accepted only when:

- exactly one JSON object parses under the documented fence normalization;
- Pydantic schema passes;
- output language matches request or has no hard mismatch;
- all evidence quotes are exact source substrings after NFC comparison;
- cross-field certainty/evidence rules pass;
- no hard safety violation is detected;
- validation status is valid or valid_with_warnings.

Warnings do not become hidden successes. Store issue codes. Important codes include:

- EMPTY_INPUT;
- INPUT_TOO_LONG;
- INVALID_JSON;
- MULTIPLE_JSON_OBJECTS;
- SCHEMA_MISSING_FIELD;
- SCHEMA_TYPE_ERROR;
- UNSUPPORTED_ENUM;
- OUTPUT_LANGUAGE_MISMATCH;
- EVIDENCE_EMPTY;
- EVIDENCE_NOT_IN_SOURCE;
- CAUSE_EVIDENCE_MISSING;
- SEVERITY_SUPPORT_WEAK;
- UNSUPPORTED_DETAIL_SUSPECTED;
- RISKY_RECOMMENDATION;
- TIMEOUT_EXHAUSTED;
- RATE_LIMIT_EXHAUSTED;
- AUTHENTICATION_FAILED;
- REFINEMENT_FAILED;
- ENCODING_ERROR.

## Explanation in Simple Words

The model’s answer is a draft until checks pass. Evidence and safety problems cannot be hidden by attractive formatting.

---

# 13. Dataset Handoff

The five records in the specification are examples, not the complete dataset. Build the real data using dataset_design.md:

1. 40-row matrix.
2. Gold labels independent of model output.
3. Natural EN/ZH pair.
4. Evidence spans per source.
5. Translation review.
6. Development/evaluation split by pair.
7. Leakage/similarity audit.
8. Validation and manifest/hash.
9. Freeze version 1.

Never use evaluation labels to choose few-shot examples or tune prompts. If a report is ambiguous enough that two labels are equally correct, either revise it before freeze or record acceptable alternatives and update metric policy before the run.

## Explanation in Simple Words

The real dataset still needs to be written and reviewed. The specification gives examples and rules, but it does not pretend 80 records already exist.

---

# 14. Evaluation Handoff

Primary metrics:

- end-to-end category success and conditional category accuracy;
- end-to-end severity success and conditional severity accuracy;
- first-pass JSON validity;
- exact evidence grounding;
- bilingual consistency;
- total latency;
- primary failure rate.

Secondary:

- field concept P/R/F1;
- completion;
- repair-assisted validity;
- manual rubric;
- substantive hallucination;
- category/language breakdown;
- initial versus refined changes;
- optional judge/repeats/statistics.

Every metric record needs numerator, denominator, exclusions, source, and version. Manual outputs are blinded. Read evaluation_plan.md for formulas.

## Explanation in Simple Words

Calculate the main measurements first and always show how many records they use. Extra analyses are useful only if they remain clearly labeled.

---

# 15. Testing Handoff

Default command must make zero network calls. Use:

- scripted FakeLLMProvider;
- temporary SQLite DB;
- injected clock/sleeper/jitter;
- saved bilingual valid/invalid fixtures;
- optional live_api marker excluded by default.

Minimum critical tests:

- empty/long/EN/ZH/mixed input;
- valid, malformed, fenced, multiple, missing, extra, wrong-type JSON;
- unsupported enum;
- missing/false evidence;
- prompt injection;
- timeout/rate-limit/auth;
- Chinese JSON/CSV/SQLite/download round trip;
- exactly one refinement cycle;
- failed refinement no third call;
- repair metrics separation;
- development-only few-shot examples;
- split pairing/leakage;
- batch interruption/resume;
- metric arithmetic and zero denominators;
- five-page Streamlit smoke.

Do not claim tests pass until they are actually run.

## Explanation in Simple Words

Tests replace the paid model with predictable answers. They make normal and failure behavior repeatable.

---

# 16. UI Handoff

Implement all states in ui_wireframes.md:

- empty;
- invalid input;
- loading;
- valid with warnings;
- invalid model output;
- provider failure;
- comparison partial failure;
- batch manifest/running/interrupted/complete;
- dashboard empty/filtered/missing manual review.

Display principles:

- evidence near relevant claims;
- invalid diagnostic output clearly labeled;
- first-pass vs repair visible;
- self initial/final visible;
- numerator/denominator in dashboard;
- no missing metric shown as zero;
- UTF-8 JSON download;
- no fake progress percentage for a single API call.

## Explanation in Simple Words

The user needs clear error screens as much as success screens. The wireframes show both.

---

# 17. Logging and Storage Handoff

Store:

- model/provider/config;
- strategy/refinement variant;
- prompt/schema/data versions and hashes;
- languages/path;
- UTC timestamps/latency;
- retry/attempts;
- raw/parsed responses;
- validation issues;
- automatic/manual metrics.

Do not store:

- API key;
- authorization headers;
- full environment dump;
- private raw ad hoc report by default;
- hidden provider secrets.

Use migrations. Make attempt records immutable. Add a deletion/export path for local ad hoc records. Use transactions per attempt/outcome and stable task IDs for resume.

## Explanation in Simple Words

Storage is an audit history. It should remember what happened without collecting secrets or unnecessary private text.

---

# 18. Implementation Verification Gates

## Gate A - Offline Core

- schema and validators tested;
- fake provider complete;
- one analysis works;
- no network;
- raw/parsed persistence works.

## Gate B - Strategy Core

- zero/few/self work through same service;
- prompt IDs/hashes recorded;
- self exactly two semantic calls;
- repair separated;
- comparison page works in fake mode.

## Gate C - Dataset and Batch

- 40 pairs reviewed/validated;
- manifest/hash;
- few-shot leakage test;
- fake full batch and resume;
- metric fixtures reconcile.

## Gate D - Live Readiness

- current provider/model decision;
- privacy/cost review;
- bounded timeout/retry;
- secret scan;
- all default tests pass;
- prompt/data/schema/concept map frozen.

## Gate E - Results

- real run complete or transparently partial;
- counts reconcile;
- manual review provenance;
- charts generated;
- honest interpretation.

## Gate F - Publication

- clean clone;
- real screenshots;
- README actual state;
- no secret/private data;
- publication checklist complete;
- explicit user authorization.

## Explanation in Simple Words

Gates are stopping points. Do not begin expensive evaluation or public release until earlier safety and correctness checks are complete.

---

# 19. Expected Final Deliverables from the Implementation Agent

When the later build is complete, report:

1. Every file created/changed.
2. Architecture decisions and deviations.
3. Commands actually run and their outcomes.
4. Tests actually passed/failed/skipped.
5. Dataset counts/hash/review status.
6. Exact run manifest/model/prompt/schema.
7. Real metrics with numerator/denominator.
8. Failure counts and limitations.
9. Real screenshot paths.
10. Secret/privacy review outcome.
11. GitHub publication status; do not publish unless authorized.
12. Remaining risks or work.

Do not say “complete” if the dataset review, real experiment, or publication gate is incomplete.

## Explanation in Simple Words

The final report should separate what was built, what was tested, what was measured, and what still needs work.

---

# 20. Definition of Ready

This planning package is ready for implementation when:

- all eight required documents exist;
- project_specification.pdf opens and renders clearly;
- the deferred decisions are understood;
- the implementation agent accepts the version 1 scope;
- no one mistakes the sample records or example calculations for completed data/results.

## Explanation in Simple Words

The build can start when the documents are readable and the next agent understands that the application, dataset, tests, and results still need to be created honestly.
