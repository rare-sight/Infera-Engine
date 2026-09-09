# Contributing to Infera Engine

## Development setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install the project and development tools: `python -m pip install -e ".[dev]"`.
3. Copy `.env.example` to `.env` and set `GROQ_API_KEY` for live analysis.
4. Install hooks once: `pre-commit install`.

Run the app with `python -m streamlit run app.py`. Run the local checks with `python -m ruff check .`, `python -m ruff format --check .`, and `python -m pytest`.

## Pull requests

Keep changes focused, add or update tests for behavior changes, and do not commit `.env`, saved research in `memory/`, or credentials. CI must pass before merge.
