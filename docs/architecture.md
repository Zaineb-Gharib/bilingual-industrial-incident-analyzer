# Architecture

## Design goal

The system separates model access from research logic. Replacing a provider must not require
rewriting prompts, schemas, validators, metrics, persistence, or Streamlit pages.

## Request flow

1. The UI or CLI creates an `AnalysisRequest`.
2. `PromptManager` loads versioned templates, inserts the report as untrusted data, includes
   the strict JSON schema, and hashes the rendered prompt.
3. `AnalysisService` calls the provider protocol through a bounded retry loop.
4. The parser accepts a direct JSON object or normalizes one outer Markdown fence. It rejects
   prose wrapping, arrays, and multiple objects.
5. Pydantic rejects missing, mistyped, unsupported, or extra fields.
6. Deterministic validators check output language, exact evidence substrings, suspicious
   numeric details, cause support, and known dangerous action patterns.
7. One syntax repair may run for repairable JSON/schema failures. Grounding and safety errors
   are terminal rather than rewritten silently.
8. The service stores each attempt and the final attributed result.

## Prompt semantics

- Zero-shot and few-shot each make one semantic analysis call.
- Self-refinement always makes an initial and one refined call. A failed refined result is not
  silently replaced with the initial answer.
- Transport retries repeat the same semantic stage and are counted separately.
- JSON repair is separately attributed and never counted as first-pass validity.

## Storage model

SQLite contains append-oriented analysis, attempt, batch-run, metric, and manual-review
tables. Batch manifests freeze dataset/prompt/schema versions, provider/model settings,
task IDs, and the dataset hash. A task ID is stable across reruns, so completed tasks can be
skipped safely.

Raw user input defaults to off. Synthetic versioned batch inputs are stored to make research
artifacts auditable. Credentials never enter a record.

## Evaluation boundaries

Automatic formulas are pure functions over stored rows and gold records. Manual reviews use
a separate blinded template. Optional LLM judges, if added later, must remain a third source
and cannot overwrite automatic or human values.

## Failure taxonomy

Input, authentication, rate-limit, timeout, provider, invalid JSON, schema, grounding, safety,
refinement, encoding, and internal failures have controlled values. Provider exceptions are
translated at the adapter boundary, sanitized, and stored without credentials.

