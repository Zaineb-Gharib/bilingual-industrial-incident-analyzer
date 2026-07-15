# Release Checklist

## Repository

- [x] Canonical root contains application, data, tests, screenshots, and documentation.
- [x] `.env`, `.venv`, local SQLite databases, caches, and raw private outputs are ignored.
- [x] `git status` and every tracked file have been reviewed.
- [x] Secret scan passes and `.env` is not tracked.
- [x] License, changelog, contribution guide, and version are current.

## Product

- [x] All five workflow pages start and every required control is usable.
- [x] Four language paths and three strategies are manually verified in demo mode.
- [x] Validation warnings, exact evidence, downloads, batch checkpoint/resume, and dashboard
  are verified.
- [x] Screenshots are legible, actual, synthetic, secret-free, and manifest-linked.

## Research integrity

- [x] Dataset hash, split, balance, provenance, review status, and few-shot IDs validate.
- [x] Demo and live values are unmistakably separated.
- [x] Metric denominators, exclusions, formula versions, and data sources are present.
- [x] Missing human review remains missing, not zero.
- [x] Live provider gate and actual demo-run failure counts are documented.

## Quality gates

- [x] Ruff formatting and lint pass.
- [x] Unit/integration tests and Streamlit smoke tests pass without network calls.
- [x] Dataset validator, UTF-8 checks, and secret scan pass.
- [x] Clean documented install and startup commands are verified.

## Publication

- [x] `gh auth status` shows exactly `Zaineb-Gharib`.
- [x] No unrelated remote/repository will be overwritten.
- [x] README clearly says the working release is demo mode, not a live-model experiment.
- [x] Public repository, README source, and referenced screenshot assets are verified through
  GitHub's API.
- [x] Suitable repository topics are added.

This is a publishable **demo-mode portfolio release**. A real-provider credential, live
experiment, cost approval, and independent human review remain future work; their absence
does not prevent publication because no live-model performance claim is made.

Published URL: `https://github.com/Zaineb-Gharib/bilingual-industrial-incident-analyzer`
