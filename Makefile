.PHONY: install lint format test check run docker-build
install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"
lint:
	python -m ruff check .
	python -m ruff format --check .
format:
	python -m ruff check --fix .
	python -m ruff format .
test:
	python -m pytest
check: lint test
run:
	python -m streamlit run app.py
docker-build:
	docker build --tag infera-engine:local .
