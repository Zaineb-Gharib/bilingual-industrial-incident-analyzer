# Implementation Checklist

**Project:** Bilingual Industrial Incident Analyzer  
**Purpose:** Small, ordered tasks for the future coding agent  
**Rule:** This checklist describes implementation work. It does not claim that the work has been performed.

Use one branch or small commit per numbered task when practical. Do not start a later phase merely because its UI is more visible. Mark a checkbox only after its verification and definition of done are satisfied.

## Working Rules

- Keep Streamlit pages thin; business rules belong in src.
- Keep provider SDK types inside one adapter.
- Save raw output before normalization.
- Make no paid/network calls in the default test suite.
- Treat evaluation labels as held out after prompts are frozen.
- Never commit .env, API keys, local databases, or private reports.
- Do not write a result into README until it comes from an archived real run.

---

# Phase 1 - Environment and Repository Setup

## 1.1 Create the repository skeleton

- [ ] **Goal:** Establish every top-level folder before feature code.
- **Files:** app.py, pages/, src/, data/, evaluation/, tests/, scripts/, results/, screenshots/, docs/.
- **Exact work:** Create the tree in project_specification.md Section 17; add package marker files if the chosen packaging approach needs them; add .gitkeep only for intentionally empty tracked folders.
- **Expected output:** Imports have predictable locations and generated/private paths are visually distinct.
- **Verify:** Run a file-tree command and compare every path with Section 17.
- **Common mistakes:** Putting application logic in scripts; tracking an empty local database; creating several competing source roots.
- **Definition of done:** A new contributor can point to the correct future location for UI, core code, data, tests, docs, and results.

## 1.2 Define Python and dependency management

- [ ] **Goal:** Make local setup reproducible for a beginner.
- **Files:** pyproject.toml, requirements.txt.
- **Exact work:** Require Python 3.11+; list direct runtime dependencies such as Streamlit, Pydantic v2, Pandas, Plotly, python-dotenv or pydantic-settings, the selected provider SDK, and a SQLite helper only if needed; list development dependencies such as Pytest, coverage, and Ruff. Keep pyproject.toml authoritative for tool configuration and provide requirements.txt as the simple install path.
- **Expected output:** One clean virtual-environment installation command.
- **Verify:** Install in a fresh virtual environment and import each direct dependency.
- **Common mistakes:** Mixing Pydantic v1 examples with v2; pinning every transitive dependency manually; failing to document platform-specific setup.
- **Definition of done:** The documented install succeeds from a clean clone.

## 1.3 Add secret-safe configuration

- [ ] **Goal:** Read keys and settings without embedding them in code.
- **Files:** src/config.py, .env.example, .gitignore, tests/unit/test_config.py.
- **Exact work:** Implement typed settings; define provider, model, timeout, transport retries, temperature, token limit, raw-input storage, DB path, and log level; make the API key optional in fake mode and required only for a live adapter; ignore .env and local data.
- **Expected output:** Helpful validation errors with no key value echoed.
- **Verify:** Test fake mode with no key, live mode with missing key, environment override precedence, and redacted repr.
- **Common mistakes:** Loading .env in library modules repeatedly; naming a real model as a permanent default; printing all environment variables.
- **Definition of done:** No secret is required to run tests or fake demo mode.

## 1.4 Create a placeholder Streamlit shell

- [ ] **Goal:** Prove navigation and configuration load before feature work.
- **Files:** app.py and five page files.
- **Exact work:** Set title/icon/layout once; add privacy notice and placeholder navigation; display non-secret provider/model configuration health.
- **Expected output:** All pages load without a provider call.
- **Verify:** Start Streamlit and visit each page; add a smoke test if supported.
- **Common mistakes:** Executing a model request during module import; duplicating global configuration.
- **Definition of done:** Placeholder UI starts from the documented command.

## Explanation in Simple Words

Phase 1 creates a safe empty project that can be installed and opened. It proves the basic setup before model logic is added.

---

# Phase 2 - Data Model and Schema

## 2.1 Implement enums and incident models

- [ ] **Goal:** Turn the JSON contract into executable Pydantic v2 models.
- **Files:** src/domain/enums.py, src/schemas/incident.py.
- **Exact work:** Implement all enums, nested Cause, RecommendedAction, EvidenceItem, Confidence, and IncidentAnalysis; forbid extra keys; trim strings; set length/list bounds; use schema_version 1.0.
- **Expected output:** A single source of truth for accepted analysis JSON.
- **Verify:** Parse a valid English and Chinese fixture and serialize them without ASCII escaping.
- **Common mistakes:** Letting arbitrary strings into enums; making evidence optional; translating enum codes.
- **Definition of done:** Models match the project specification exactly or an approved decision note explains changes.

## 2.2 Implement cross-field issue types

- [ ] **Goal:** Represent validation problems consistently.
- **Files:** src/domain/models.py, src/schemas/run_records.py.
- **Exact work:** Define ValidationIssue with code, field path, severity, safe message, technical detail, and retryability; define ValidationStatus; define AnalysisRequest, AttemptRecord, and AnalysisOutcome.
- **Expected output:** UI, logs, storage, and tests use the same failure vocabulary.
- **Verify:** Serialize issue fixtures and confirm technical detail can be omitted from user display.
- **Common mistakes:** Passing raw exceptions to UI; representing warnings as unstructured strings only.
- **Definition of done:** Every planned error maps to one documented issue code.

## 2.3 Build schema fixtures and tests

- [ ] **Goal:** Lock down required behavior before provider integration.
- **Files:** tests/fixtures/analysis_*.json, tests/unit/test_incident_schema.py.
- **Exact work:** Add valid EN/ZH/cross-language fixtures; missing fields; nulls; wrong list types; empty evidence; blank items; extra fields; unsupported category/severity/team; too-long fields.
- **Expected output:** Parameterized tests that explain why each invalid object fails.
- **Verify:** Run the schema test file alone.
- **Common mistakes:** Testing only happy paths; asserting fragile full error strings rather than error locations/types.
- **Definition of done:** All required schema edge cases have a named test.

## Explanation in Simple Words

Phase 2 defines the strict form for model answers and tests bad forms. Later features can trust one shared data contract.

---

# Phase 3 - Dataset Creation

## 3.1 Design the scenario matrix

- [ ] **Goal:** Balance content before writing 40 pairs.
- **Files:** data/scenario_matrix_v1.csv, docs/dataset_card.md.
- **Exact work:** Allocate four pairs per category; one development and three evaluation; balance severity, explicit/suspected/unknown cause, length, and industrial versus software setting; reserve stable IDs.
- **Expected output:** Forty planned rows with no report text yet.
- **Verify:** Pivot counts by category/split/severity and review for gaps.
- **Common mistakes:** Writing many server outages first and forcing balance later; using critical too often.
- **Definition of done:** Matrix totals and balance rules pass review.

## 3.2 Draft and label source scenarios

- [ ] **Goal:** Create realistic fictional facts and gold labels independent of model behavior.
- **Files:** data/incidents_v1_draft.jsonl.
- **Exact work:** Write short reports; label category, severity, systems, concept IDs, certainty, action concepts, teams, exact evidence spans, safety and ambiguity notes; record author/reviewer status.
- **Expected output:** Forty complete source-language scenario records.
- **Verify:** A human can derive every label from the report and rubric.
- **Common mistakes:** Putting a gold cause in labels when report says unknown; adding unsafe procedural actions.
- **Definition of done:** No label was copied from or adjusted to a model answer.

## 3.3 Produce and review paired translations

- [ ] **Goal:** Preserve meaning across English and Simplified Chinese.
- **Files:** data/incidents_v1_draft.jsonl, review worksheet.
- **Exact work:** Translate facts, certainty, time, impact, and negation; mark exact evidence independently in each language; perform bilingual comparison; record disagreements and resolution.
- **Expected output:** Every scenario has meaning-equivalent EN/ZH source and labels.
- **Verify:** Sentence-level checklist; optional back-translation; spot-check numbers and negatives.
- **Common mistakes:** Translating evidence spans instead of selecting source substrings; making Chinese text more certain.
- **Definition of done:** translation_review_status is approved or transparently single_reviewer.

## 3.4 Validate leakage, balance, and reproducibility

- [ ] **Goal:** Freeze a clean dataset.
- **Files:** src/schemas/dataset.py, scripts/validate_dataset.py, data/dataset_manifest_v1.json.
- **Exact work:** Check types/enums/IDs, split pairing, evidence containment, category counts, concept IDs, UTF-8/NFC, shingle overlap, duplicates; emit counts and SHA-256; generate flat CSV from JSONL.
- **Expected output:** incidents_v1.jsonl, generated CSV, manifest, and validation report.
- **Verify:** Run validator twice and compare hash/output.
- **Common mistakes:** Editing generated CSV as source; moving one translation to a different split.
- **Definition of done:** Dataset v1 is read-only for the primary experiment.

## Explanation in Simple Words

Phase 3 creates the practice and exam data. English and Chinese versions remain together, and labels are written before model results can influence them.

---

# Phase 4 - LLM Provider Interface

## 4.1 Define neutral provider contracts

- [ ] **Goal:** Prevent architecture lock-in.
- **Files:** src/providers/base.py.
- **Exact work:** Define LLMRequest, LLMResponse, LLMProvider Protocol, usage metadata, structured-output capability flags, and internal exception taxonomy.
- **Expected output:** Core modules can type-check without a vendor SDK.
- **Verify:** Search src excluding providers/adapters and confirm no vendor imports.
- **Common mistakes:** Returning an SDK response object; hiding resolved model/finish reason.
- **Definition of done:** A second adapter could be written using base.py alone.

## 4.2 Implement deterministic fake provider

- [ ] **Goal:** Test every workflow offline.
- **Files:** src/providers/fake.py, tests/unit/test_fake_provider.py.
- **Exact work:** Accept a queue of response strings/exceptions; record requests; support optional latency/usage metadata; expose call count; provide safe default fixtures.
- **Expected output:** Tests can script success, timeout, rate limit, malformed JSON, and refinement.
- **Verify:** Contract tests and no network socket use.
- **Common mistakes:** Hard-coding one response globally; sleeping in tests.
- **Definition of done:** Every planned provider failure can be reproduced deterministically.

## 4.3 Implement one reference adapter and factory

- [ ] **Goal:** Make one real provider usable without infecting core code.
- **Files:** src/providers/reference_provider.py, factory.py.
- **Exact work:** Map neutral request to current SDK; set timeout; request structured output when selected; map auth/rate/timeout/server errors; collect safe IDs/usage/latency; return plain neutral response.
- **Expected output:** A provider chosen by configuration.
- **Verify:** Mock SDK contract tests; one opt-in sanitized live smoke test later.
- **Common mistakes:** Assuming provider-specific JSON mode exists everywhere; logging headers.
- **Definition of done:** Factory returns fake or real adapter without service changes.

## Explanation in Simple Words

Phase 4 gives all model providers one common interface. Most development and testing use a free, predictable fake provider.

---

# Phase 5 - Prompt Templates

## 5.1 Create immutable prompt files

- [ ] **Goal:** Move instructions out of Python strings.
- **Files:** src/prompts/*.txt.
- **Exact work:** Transcribe the approved shared, zero-shot, few-shot, self-initial, combined review-and-correct, JSON repair, EN, and ZH modules; include schema/enums and injection rules.
- **Expected output:** Reviewable prompt version v1.
- **Verify:** Test required clauses and output JSON shape.
- **Common mistakes:** Omitting exact-evidence rule from one strategy; making prompt behavior differ beyond strategy.
- **Definition of done:** All prompt text is versioned and hashed.

## 5.2 Build safe PromptManager

- [ ] **Goal:** Render prompts with explicit trust boundaries.
- **Files:** src/prompts/manager.py, tests/unit/test_prompt_manager.py.
- **Exact work:** Load templates; insert schema and language module; serialize reports safely in a user message; return system/user messages, prompt version/hash, and example IDs.
- **Expected output:** Provider-ready PromptPackage.
- **Verify:** Injection string remains only inside the report data block; braces/Chinese survive.
- **Common mistakes:** String-format errors from report braces; embedding report in system prompt.
- **Definition of done:** Four language paths render in every strategy.

## 5.3 Freeze few-shot bank

- [ ] **Goal:** Demonstrate behavior without leakage.
- **Files:** src/prompts/examples_v1.json.
- **Exact work:** Select four development IDs covering both languages/outputs and unknown/explicit cause; include expected JSON; validate example schema and split membership.
- **Expected output:** Stable few-shot example list recorded in run metadata.
- **Verify:** Automated leakage test asserts split=development and no high-overlap evaluation pair.
- **Common mistakes:** Picking examples after viewing evaluation results.
- **Definition of done:** Example bank is frozen with prompt v1.

## Explanation in Simple Words

Phase 5 stores prompts as versioned experiment inputs. It also prevents held-out exam examples from entering the few-shot prompt.

---

# Phase 6 - Single Incident Analysis

## 6.1 Implement request prechecks

- [ ] **Goal:** Reject unsafe/invalid input before cost.
- **Files:** src/services/analysis_service.py, src/validation/language.py, src/utils/text.py.
- **Exact work:** Trim for emptiness; enforce 10-4,000 characters; preserve original; create NFC comparison copy; calculate language hint; build correlation ID.
- **Expected output:** Valid AnalysisRequest or structured issue.
- **Verify:** Empty/long/EN/ZH/mixed tests and provider call count zero on rejection.
- **Common mistakes:** Normalizing and losing original evidence positions.
- **Definition of done:** FR-001 through FR-006 are tested.

## 6.2 Orchestrate one zero/few-shot call

- [ ] **Goal:** Create a reusable happy path.
- **Files:** analysis_service.py, prompt manager, provider, validator interfaces.
- **Exact work:** Render, call, time, save raw response, parse/validate, assemble outcome; keep strategy-specific policy in small methods.
- **Expected output:** Fake response becomes validated IncidentAnalysis.
- **Verify:** End-to-end integration test with expected metadata.
- **Common mistakes:** Returning provider exception directly; losing first raw response.
- **Definition of done:** Same service handles zero and few-shot through strategy selection.

## 6.3 Add storage and JSON download model

- [ ] **Goal:** Persist an auditable record and safe export.
- **Files:** storage database/repositories, migrations, page 1.
- **Exact work:** Create tables for runs, analyses, attempts, validation issues, and outputs; save transactionally; build export object; use ensure_ascii false and application/json.
- **Expected output:** Reloadable outcome and correct Chinese download.
- **Verify:** Temporary SQLite integration test and JSON round trip.
- **Common mistakes:** Storing only final parsed object; using CSV as primary nested storage.
- **Definition of done:** Raw and parsed forms are linked by IDs.

## 6.4 Build Single Analysis page

- [ ] **Goal:** Expose the use case without adding core logic to UI.
- **Files:** pages/1_single_analysis.py and UI helpers.
- **Exact work:** Input, counters, selections, privacy control, submit spinner, status/result/evidence/warnings/metadata, JSON download, session-state double-submit guard.
- **Expected output:** Beginner-readable analysis screen.
- **Verify:** Fake-mode manual walkthrough for four language paths.
- **Common mistakes:** Hiding invalid evidence; using color alone for severity.
- **Definition of done:** Page behavior satisfies FR-030 through FR-034 relevant items.

## Explanation in Simple Words

Phase 6 connects one report to the service, validation, storage, and UI. It produces the first complete fake-mode workflow.

---

# Phase 7 - Validation and Retries

## 7.1 Implement strict parser and schema validation

- [ ] **Goal:** Separate raw text, parsed JSON, and schema result.
- **Files:** validation/parser.py, schema_validator.py.
- **Exact work:** Direct parse; optional single-fence removal with audit flag; reject prose/multiple objects; call Pydantic; map errors to safe issue codes.
- **Expected output:** Deterministic ParseOutcome.
- **Verify:** Valid, fenced, truncated, multiple-object, wrong-type fixtures.
- **Common mistakes:** Greedy regex object extraction; unsafe eval.
- **Definition of done:** Parser never guesses between ambiguous candidates.

## 7.2 Implement evidence, language, and safety validation

- [ ] **Goal:** Check report-dependent rules.
- **Files:** grounding.py, language.py, safety.py.
- **Exact work:** NFC containment per quote; supported field names; cause-evidence consistency; script-ratio language warning; configurable risky-action patterns; named-number heuristic warning.
- **Expected output:** Structured hard errors and review warnings.
- **Verify:** English/Chinese punctuation, missing/false evidence, high severity without support, risky action tests.
- **Common mistakes:** Claiming heuristic warnings prove hallucination.
- **Definition of done:** Hard evidence failures are never displayed as grounded.

## 7.3 Implement transport retry

- [ ] **Goal:** Recover from temporary failures without unbounded calls.
- **Files:** service retry helper, timing utilities.
- **Exact work:** Retry only rate/timeouts/transient server errors; use Retry-After or 1/2 second backoff+jitter; inject sleeper/jitter; enforce overall deadline; save every attempt.
- **Expected output:** Success-after-retry and terminal failure outcomes.
- **Verify:** Call counts and zero-wait fake tests.
- **Common mistakes:** Retrying authentication; counting transport retry as semantic refinement.
- **Definition of done:** Maximum attempts are configuration-tested.

## 7.4 Implement optional syntax-only repair

- [ ] **Goal:** Improve operational usability without corrupting primary research metrics.
- **Files:** json_repair prompt, analysis service policy, tests.
- **Exact work:** Run once only for configured parse/schema problems; save repair link; forbid substantive evidence invention; validate repaired output; retain primary failure.
- **Expected output:** primary_status and final_usable_status both available.
- **Verify:** Repair success/failure tests and metric eligibility.
- **Common mistakes:** Reporting repaired validity as first-pass validity.
- **Definition of done:** Research reports can separate unassisted and assisted rates.

## Explanation in Simple Words

Phase 7 checks bad model answers and temporary API failures. Retries are limited, and repaired answers never hide the original failure.

---

# Phase 8 - Self-Refinement

## 8.1 Implement initial stage

- [ ] **Goal:** Save the initial answer and deterministic feedback.
- **Files:** analysis service self strategy, initial prompt.
- **Exact work:** Run first semantic call, validate even if raw is malformed, store parsed/raw/errors, create safe warnings JSON.
- **Expected output:** Auditable initial stage.
- **Verify:** Valid and malformed initial response tests.
- **Common mistakes:** Discarding invalid initial response.
- **Definition of done:** Initial metrics can be computed independently.

## 8.2 Implement one combined review-and-correct stage

- [ ] **Goal:** Give exactly one semantic correction opportunity.
- **Files:** self_refine_v1.txt, analysis service, run models.
- **Exact work:** Render original report, initial response, and validator warnings; request a complete final object; validate and store; set refinement_cycles=1.
- **Expected output:** Linked initial/final output with per-call latency.
- **Verify:** Absent transport retries, fake provider call count is exactly two.
- **Common mistakes:** Separate third call for final answer; changing output language.
- **Definition of done:** No branch can start another semantic refinement.

## 8.3 Add self-refinement comparison display

- [ ] **Goal:** Make changes transparent.
- **Files:** page 1 expander, comparison helpers.
- **Exact work:** Show initial/final statuses, changed fields, warnings addressed/new, and latencies; label invalid raw diagnostic output.
- **Expected output:** User sees what refinement changed.
- **Verify:** Fake fixture with one fixed and one newly introduced issue.
- **Common mistakes:** Showing only the better-looking final output.
- **Definition of done:** Both stages remain inspectable.

## Explanation in Simple Words

Phase 8 lets the model check its answer once. Both the first and corrected answers are saved, and no infinite loop is possible.

---

# Phase 9 - Batch Evaluation

## 9.1 Build dataset loader and task builder

- [ ] **Goal:** Convert paired records into a stable balanced run.
- **Files:** dataset_loader.py, task_builder.py.
- **Exact work:** Validate hash/version; expand EN/ZH; assign same output language within pair; make 15 EN-output and 15 ZH-output pairs; create stable task IDs; rotate strategy order deterministically.
- **Expected output:** 60 tasks, 180 strategy outputs planned, all four language paths represented 15 times.
- **Verify:** Count assertions and stable snapshot from fixed seed.
- **Common mistakes:** Random assignment without saving it; separating paired output languages.
- **Definition of done:** Rebuilding from the manifest produces identical tasks.

## 9.2 Implement frozen run manifest

- [ ] **Goal:** Make every experiment auditable.
- **Files:** run manifest schema, evaluation/manifests/.
- **Exact work:** Save dataset/prompt/schema hashes, model settings, tasks/order, code commit, retry and repair policy, timestamp, privacy mode.
- **Expected output:** Immutable manifest before first call.
- **Verify:** Resume with one changed setting must fail with a clear mismatch.
- **Common mistakes:** Reading current config during resume instead of manifest config.
- **Definition of done:** Every result references one manifest hash.

## 9.3 Implement resumable batch runner

- [ ] **Goal:** Preserve expensive progress.
- **Files:** batch_service.py, scripts/run_evaluation.py.
- **Exact work:** Query pending task-strategy IDs; save after each; handle cancellation after current item; limit concurrency conservatively; summarize failures; support fake full run.
- **Expected output:** Interruptible/resumable result set with no duplicates.
- **Verify:** Stop midway, restart, compare with uninterrupted fake run.
- **Common mistakes:** Holding all results in memory/session state; retrying failed semantic tasks on resume without policy.
- **Definition of done:** Resume is idempotent.

## 9.4 Build Batch Evaluation page

- [ ] **Goal:** Provide safe progress and quota awareness.
- **Files:** pages/3_batch_evaluation.py.
- **Exact work:** Show manifest preview, task/call estimate, confirmation, start/resume, progress, failure counts, cancel-after-current, download links.
- **Expected output:** Researcher can understand cost and state before starting.
- **Verify:** Fake batch smoke test and refresh/resume.
- **Common mistakes:** Starting on page load; promising exact call count despite retries.
- **Definition of done:** No accidental live batch starts.

## Explanation in Simple Words

Phase 9 runs the held-out dataset in a fixed, resumable order. A saved manifest acts like a receipt for the experiment.

---

# Phase 10 - Metrics and Review

## 10.1 Implement pure automatic metrics

- [ ] **Goal:** Calculate exact metrics with explicit eligibility.
- **Files:** evaluation/metrics.py, tests/unit/test_metrics.py.
- **Exact work:** Category/severity/exact match, concept P/R/F1, first/final JSON validity, completion, evidence grounding, evidence-quote hallucination, consistency, latency summaries, failure breakdown.
- **Expected output:** Tidy rows: run, group, metric, numerator, denominator, value, source, version.
- **Verify:** Hand-calculated fixtures including zero denominators.
- **Common mistakes:** Averaging group percentages with unequal denominators.
- **Definition of done:** Every value can be recomputed from exported records.

## 10.2 Implement concept normalization

- [ ] **Goal:** Compare bilingual text fields practically.
- **Files:** evaluation/concept_map_v1.json, normalization helper.
- **Exact work:** Define acceptable EN/ZH phrases per gold concept; NFC, lowercase English, collapse whitespace; preserve map version; avoid overly broad synonyms.
- **Expected output:** Deterministic symptom/action concept matches.
- **Verify:** Positive/negative bilingual fixtures and manual false-match review.
- **Common mistakes:** Using one substring such as “fail” for many concepts.
- **Definition of done:** Map is frozen with primary evaluation labels.

## 10.3 Build manual review workflow

- [ ] **Goal:** Evaluate cause, actions, language quality, and substantive hallucination.
- **Files:** manual_review.py, evaluation/rubrics/manual_review_v1.md, CSV template.
- **Exact work:** Export blinded randomized rows; include source/gold/output; collect 0-2 dimensions, claim-unit counts, reviewer ID, notes; validate imports; never overwrite model records.
- **Expected output:** Versioned review table linked to output IDs.
- **Verify:** Round-trip a sample; duplicate/reviewer validation.
- **Common mistakes:** Showing strategy name to reviewer; silently treating blanks as zero.
- **Definition of done:** Manual scores have provenance and can be excluded/revised transparently.

## 10.4 Generate result tables

- [ ] **Goal:** Produce publication-ready data before charts.
- **Files:** reporting.py, scripts/export_results.py, results/processed/.
- **Exact work:** Group by strategy/language/category; emit denominators/exclusions; make primary/secondary tables; separate auto/manual/judge sources.
- **Expected output:** CSV/JSON tables for dashboard and README.
- **Verify:** Aggregate totals reconcile with record counts.
- **Common mistakes:** Editing exported CSV by hand.
- **Definition of done:** Charts read generated processed tables only.

## Explanation in Simple Words

Phase 10 converts saved outputs into honest measurements and a human-review queue. Every value keeps its count and source.

---

# Phase 11 - Comparison Page and Dashboard

## 11.1 Build same-input comparison

- [ ] **Goal:** Compare three strategies without declaring semantic similarity as correctness.
- **Files:** comparison_service.py, pages/2_strategy_comparison.py.
- **Exact work:** Run fixed settings; capture per-strategy outputs/calls/latency; show validity, completion, grounding, warnings, field differences; tabs/columns.
- **Expected output:** Transparent three-way view.
- **Verify:** Fake responses with deliberate field differences.
- **Common mistakes:** Running strategies with different model settings; calling longest answer best.
- **Definition of done:** Configuration appears once above the comparison and is stored.

## 11.2 Build dashboard queries and filters

- [ ] **Goal:** Slice results without recalculating them incorrectly in UI.
- **Files:** reporting queries, pages/4_results_dashboard.py.
- **Exact work:** Filters for run/strategy/input/output/path/category/severity/source; empty states; metric cards with numerator/denominator.
- **Expected output:** Correct filtered tables.
- **Verify:** Compare filtered UI counts with SQL/fixture expectations.
- **Common mistakes:** Filters affecting numerator but not denominator.
- **Definition of done:** Every displayed metric shows scope and source.

## 11.3 Build accessible charts

- [ ] **Goal:** Show important patterns clearly.
- **Files:** chart helpers, dashboard.
- **Exact work:** Grouped strategy bars, category heatmap, severity confusion matrix, latency distribution, failure stack; readable titles; non-color cues/tooltips; zero-based axes for rates where appropriate.
- **Expected output:** Downloadable Plotly charts.
- **Verify:** Visual check on narrow/wide layouts and grayscale awareness.
- **Common mistakes:** Truncated labels, misleading axis ranges, charting missing manual data as zero.
- **Definition of done:** A chart caption says metric, run, denominator, and provenance.

## Explanation in Simple Words

Phase 11 shows the three strategies and measured results clearly. Charts help people explore results without hiding missing data or failures.

---

# Phase 12 - Testing and Quality Gates

## 12.1 Complete unit and schema tests

- [ ] **Goal:** Cover all pure logic.
- **Files:** tests/unit/.
- **Exact work:** Implement T-001 through T-013, T-021 through T-025, metric and dataset edge cases.
- **Expected output:** Fast deterministic unit suite.
- **Verify:** Run twice with no network and random test order if available.
- **Common mistakes:** High coverage number with unasserted behavior.
- **Definition of done:** Every critical validator has positive and negative tests.

## 12.2 Complete integration and batch tests

- [ ] **Goal:** Verify module interactions and persistence.
- **Files:** tests/integration/.
- **Exact work:** Implement T-014 through T-020, temporary DB migrations, full fake batch, resume, export, self-refine.
- **Expected output:** Repeatable end-to-end workflows.
- **Verify:** Tests pass in a clean temporary directory.
- **Common mistakes:** Sharing test DB state; relying on test execution order.
- **Definition of done:** No integration test requires a live key.

## 12.3 Add Streamlit smoke tests

- [ ] **Goal:** Catch page import and basic interaction failures.
- **Files:** tests/integration/test_streamlit_pages.py.
- **Exact work:** Load pages in fake mode; submit valid/invalid inputs; check warnings and download; render empty dashboard and fake data.
- **Expected output:** Basic UI regression protection.
- **Verify:** Headless/default CI command.
- **Common mistakes:** Testing CSS selectors too tightly.
- **Definition of done:** All five pages load and one primary path per page works.

## 12.4 Run static and secret checks

- [ ] **Goal:** Protect code quality and repository safety.
- **Files:** Ruff config, scripts/check_secrets.py, optional CI.
- **Exact work:** Lint, format check, type check if adopted, secret patterns, forbidden tracked paths, no live marker by default.
- **Expected output:** One documented quality command.
- **Verify:** Insert a fake key pattern in a temporary fixture and confirm detection.
- **Common mistakes:** Secret-scanning only current files, not staged/history before publication.
- **Definition of done:** Quality gates pass before real evaluation.

## Explanation in Simple Words

Phase 12 tests normal and failure paths without paying for API calls. It also checks code quality and accidental secrets.

---

# Phase 13 - Documentation

## 13.1 Write beginner quick start and configuration

- [ ] **Goal:** Let a new user run fake mode first.
- **Files:** README.md, .env.example.
- **Exact work:** Clone, environment, install, fake demo, live provider opt-in, key setup, troubleshooting, Windows notes.
- **Expected output:** Copyable commands with expected safe states.
- **Verify:** Follow from a clean clone.
- **Common mistakes:** Requiring a paid key for first run.
- **Definition of done:** Beginner reaches the UI without guessing.

## 13.2 Write methods and dataset documentation

- [ ] **Goal:** Explain what results mean.
- **Files:** data/README.md, results/README.md, architecture/evaluation docs.
- **Exact work:** Dataset card, provenance, splits, leakage, metrics, repair policy, run manifest, limitations, privacy.
- **Expected output:** Research methodology independent of code.
- **Verify:** Cross-check versions/hashes/formulas.
- **Common mistakes:** Leaving planning language after implementation changes.
- **Definition of done:** Reviewer can audit the experiment design.

## 13.3 Build Project Information page

- [ ] **Goal:** Put the project story inside the app.
- **Files:** pages/5_project_information.py.
- **Exact work:** Goal, workflow, simple prompt definitions, architecture, limitations, ethics, future work, decision-support warning.
- **Expected output:** Portfolio-friendly explainer.
- **Verify:** Compare claims against README and actual results.
- **Common mistakes:** Marketing language that overstates safety.
- **Definition of done:** Page contains no unsupported result claim.

## Explanation in Simple Words

Phase 13 teaches a new user how to run and understand the real project. Documentation must match the code rather than the earlier plan.

---

# Phase 14 - Real Evaluation and Screenshots

## 14.1 Freeze and run the primary experiment

- [ ] **Goal:** Produce actual results only after code/data/prompts are final.
- **Files:** frozen manifest, results/raw/, processed/.
- **Exact work:** Record commit; validate data; estimate cost; run; preserve failures; complete manual review; generate aggregates.
- **Expected output:** Archived run with manifest, outputs, and review provenance.
- **Verify:** Counts reconcile and a second script invocation does not mutate the run.
- **Common mistakes:** Editing prompts mid-run; rerunning only failed strategies without disclosure.
- **Definition of done:** Results are traceable to a frozen commit and manifest.

## 14.2 Interpret results honestly

- [ ] **Goal:** Explain evidence without exaggeration.
- **Files:** README results, results report.
- **Exact work:** Show primary/secondary metrics, denominators, per-language/category patterns, failures, variability limitations, unexpected findings.
- **Expected output:** Balanced research narrative.
- **Verify:** Every number links to generated table.
- **Common mistakes:** Calling small differences significant; hiding the worst category.
- **Definition of done:** Placeholder text is replaced only where real data exists.

## 14.3 Capture real screenshots

- [ ] **Goal:** Show the actual running product.
- **Files:** screenshots/*.png, screenshot manifest.
- **Exact work:** Use synthetic examples; capture required states; record commit/example; redact IDs/keys; crop consistently; add alt text/captions.
- **Expected output:** Home, EN, ZH, cross-language, comparison, warning, batch, dashboard, charts, info.
- **Verify:** Reproduce each screen from manifest.
- **Common mistakes:** Creating mock screenshots; showing fake metrics as real.
- **Definition of done:** All images come from the actual app.

## Explanation in Simple Words

Phase 14 performs the real experiment only after everything is frozen. Results and screenshots come from the actual application and archived run.

---

# Phase 15 - GitHub Publication

## 15.1 Perform pre-publication security review

- [ ] **Goal:** Prevent accidental disclosure.
- **Files:** entire repository and Git history.
- **Exact work:** Secret scan current tree/history; inspect .gitignore; remove raw private input; check screenshots; verify .env example blank; review licenses.
- **Expected output:** Signed release checklist.
- **Verify:** Clean clone contains no key/private DB/report.
- **Common mistakes:** Deleting a key from current file but leaving it in history.
- **Definition of done:** No secret or confidential content is present.

## 15.2 Perform clean-clone reproducibility review

- [ ] **Goal:** Test the public experience.
- **Files:** README, dependencies, tests, data, example outputs.
- **Exact work:** Clone to new directory; install; run offline tests; launch fake demo; validate dataset; regenerate processed tables/charts where supported.
- **Expected output:** Reproducibility log with commit.
- **Verify:** A second person follows instructions if available.
- **Common mistakes:** Depending on untracked local files.
- **Definition of done:** Public steps work without the author’s machine state.

## 15.3 Publish and tag

- [ ] **Goal:** Release a professional portfolio version.
- **Files:** repository metadata, LICENSE, CHANGELOG, release notes.
- **Exact work:** Choose visibility/license; push; enable checks; verify rendered Mermaid/links/images; create v1.0.0 tag only when stable; add topics and concise description.
- **Expected output:** Public repository and release.
- **Verify:** Browse as signed-out user and test links.
- **Common mistakes:** Publishing planning placeholders as actual results.
- **Definition of done:** GitHub publication plan gate is fully checked.

## Explanation in Simple Words

Phase 15 verifies secrets, reproducibility, and honesty before publication. The repository is public only after the user authorizes that later action.

---

# Final Implementation Readiness Gate

- [ ] All deferred decisions are recorded.
- [ ] Schema, prompt, dataset, and metric versions are frozen.
- [ ] Default tests make zero network calls.
- [ ] One fake-mode end-to-end workflow is complete.
- [ ] No raw private input or key is tracked.
- [ ] Primary experiment has not started before code/data/prompt freeze.
- [ ] Real results are stored with manifest and denominators.
- [ ] Real screenshots are taken only after implementation.
- [ ] README makes the decision-support limitation prominent.
- [ ] Clean clone can reproduce the offline demo and tests.

## Explanation in Simple Words

This checklist turns the large specification into small jobs. Each job says what files to touch, what result to expect, how to test it, common mistakes, and the exact condition for marking it complete.
