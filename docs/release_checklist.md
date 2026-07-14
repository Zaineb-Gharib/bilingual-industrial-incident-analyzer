# Release Checklist

## Repository

- [ ] Canonical root contains application, data, tests, screenshots, and documentation.
- [ ] `.env`, `.venv`, local SQLite databases, caches, and raw private outputs are ignored.
- [ ] `git status` and every tracked file have been reviewed.
- [ ] Secret scan passes and `.env` is not tracked.
- [ ] License, changelog, contribution guide, and version are current.

## Product

- [ ] All five pages start and every required control is usable.
- [ ] Four language paths and three strategies are manually verified in available mode.
- [ ] Validation warnings, exact evidence, downloads, batch checkpoint/resume, and dashboard
  are verified.
- [ ] Screenshots are legible, actual, synthetic, secret-free, and manifest-linked.

## Research integrity

- [ ] Dataset hash, split, balance, provenance, review status, and few-shot IDs validate.
- [ ] Demo and live values are unmistakably separated.
- [ ] Metric denominators, exclusions, formula versions, and data sources are present.
- [ ] Missing human review remains missing, not zero.
- [ ] Live provider gate and actual failure counts are documented.

## Quality gates

- [ ] Ruff formatting and lint pass.
- [ ] Unit/integration tests and Streamlit smoke tests pass without network calls.
- [ ] Dataset validator, UTF-8 checks, and secret scan pass.
- [ ] Clean documented install and startup commands are verified.

## Publication

- [ ] `gh auth status` shows exactly `Zaineb-Gharib`.
- [ ] No unrelated remote/repository will be overwritten.
- [ ] Live empirical gate is complete before calling the public project experimentally complete.
- [ ] Public URL opens and README screenshots render.
- [ ] Topics and release tag are added only after all applicable items pass.

