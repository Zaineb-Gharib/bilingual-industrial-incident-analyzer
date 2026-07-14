# Contributing

Thank you for improving the project. Keep changes small, typed, documented, and
reproducible.

1. Create a branch from `main`.
2. Install `requirements.txt` in a virtual environment.
3. Add or update tests. Tests must use deterministic providers unless explicitly marked
   `live_api`; the default suite must make no network calls.
4. Run `make check` and `ruff format --check .`.
5. Never commit `.env`, API keys, local databases, private incident text, or unreviewed
   claims of model performance.
6. Identify artifacts as live-provider, demo-provider, test-fixture, automatic, manual, or
   pending review.
7. Explain schema, prompt, dataset, or metric version changes in `CHANGELOG.md`.

Dataset contributions must be synthetic or explicitly licensed, non-identifying, bilingual
where practical, evidence-grounded, and assigned wholly to the development or evaluation
split by scenario pair.

