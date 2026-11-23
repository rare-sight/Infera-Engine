# Infera Engine

Infera Engine is a Streamlit application for researching developing topics and
turning evidence into grounded analysis, key uncertainties, and explainable
forecast scenarios.

## Requirements

- Python 3.11 or later
- A Groq API key for analysis
- Optional: Ollama running locally if you want to route analysis and uncertainty
  extraction to a local model
- Optional: Docker and Docker Compose for a containerized run

## Quick start

Create and activate a virtual environment, then install the project and its
development tools.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Create a `.env` file in the project root and add your Groq API key:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` or share its contents. Start the application with:

```bash
python -m streamlit run app.py
```

Streamlit prints the local URL when the server starts.

## Models and rate limiting

The app uses Groq by default, with `openai/gpt-oss-120b` selected initially.
`llama-3.3-70b-versatile` is also available to Groq accounts that have access
to it. Set `GROQ_MODEL` in `.env` to select the initial sidebar model.

The sidebar can optionally route the analysis and uncertainty stages through
Ollama. Scenario generation, entity resolution, research planning and synthesis,
and scenario critique continue to use Groq. Set `OLLAMA_BASE_URL` or
`OLLAMA_MODEL` in `.env` to configure the local Ollama endpoint and initial
model; the defaults are `http://localhost:11434` and `qwen3:8b`.

Groq requests share a process-local rolling budget of up to 8,000 estimated
tokens per 60 seconds, including prompt and output tokens. Calls proceed without
a fixed delay when budget is available and wait when recent usage requires it.
The limiter reserves the requested output allowance and reconciles it with
provider-reported usage when available. It cannot account for requests made by
other applications or users sharing the same Groq quota.

## Workflow

The LangGraph workflow runs these stages in order:

1. Resolve a provisional entity card for the topic.
2. Plan research questions, search the web, and synthesize the findings.
3. Reconcile the entity card against the research.
4. Analyze the research and identify key uncertainties.
5. Generate three structured scenarios and a qualitative red-team critique.

The research stage uses web search results and asks the model to cite sources.
Check the source links and dates, especially for current figures and forecasts.
Scenario records include a time horizon, forecast, evidence for and against,
and 3–6 evidence factors. The app does not assign an overall scenario
confidence or probability rating.

After a run, the app attempts to save the research and analysis as JSON files
under `memory/`. These files are local application data; do not commit sensitive
or private research.

## Docker

Create the `.env` file as described above, then run:

```bash
docker compose up --build
```

Open `http://localhost:8501`. The compose configuration passes `.env` values
into the container.

## Development and CI

Run the same checks locally with:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m pip check
```

GitHub Actions runs linting, formatting, tests, and dependency validation for
pull requests and pushes to `main` or `master` across Python 3.11, 3.12, and
3.13. CodeQL scans Python on pushes, pull requests, and a weekly schedule.
Dependabot checks Python and GitHub Actions dependencies weekly. Pushing a
version tag such as `v0.1.0` publishes a container image to GitHub Container
Registry.

## Project layout

```text
core/
  agents/       Research planner, researcher, entity resolver, critic
  nodes/        LangGraph workflow stages
  tools/        Web search
  graph.py      Workflow construction
  models.py     Groq/Ollama configuration and Groq token-budget handling
  state.py      Workflow state and structured output schemas
ui/             Streamlit presentation components and styles
utils/          Application utilities
tests/          Automated tests
app.py          Streamlit application entry point
pyproject.toml  Dependencies and tool configuration
```

## Disclaimer

Infera Engine supports research and decision-making; it does not guarantee that
web sources are complete or that forecasts will occur. Treat generated
scenarios as analysis, verify important claims against their sources, and do
not use them as a substitute for professional advice.

## License

MIT License. See [LICENSE](./LICENSE).
