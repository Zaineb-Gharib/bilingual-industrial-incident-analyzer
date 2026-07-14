.PHONY: install format lint test validate run demo-eval check

install:
	python -m pip install -r requirements.txt

format:
	ruff format .

lint:
	ruff check .

test:
	pytest

validate:
	python scripts/validate_dataset.py
	python scripts/check_secrets.py

run:
	streamlit run app.py

demo-eval:
	python scripts/run_evaluation.py --provider demo --model demo-v1 --split development

check: lint test validate
