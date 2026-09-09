# Infera Engine

An evidence-driven multi-agent reasoning system for analyzing evolving events, evaluating competing hypotheses, and generating explainable forecasts.

## Quick start

Python 3.11 or later is required. Create and activate a virtual environment, then install the application and development tools:

```bash
python -m pip install -e ".[dev]"
copy .env.example .env  # Windows
python -m streamlit run app.py
```

Set `GROQ_API_KEY` in `.env` before running an analysis. The sidebar lets users choose Groq's `openai/gpt-oss-120b` (the supported developer-tier default) or `llama-3.3-70b-versatile` for Groq accounts that have access to that Llama model. Users can also opt into Ollama for only the lower-power analysis and uncertainty stages; all other stages remain on Groq. Set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` in `.env` when using that option.

For a containerized local run, copy `.env.example` to `.env`, fill in the key, and run `docker compose up --build`. The app is then available at `http://localhost:8501`.

## Quality and delivery

GitHub Actions runs linting, formatting, tests, and dependency validation for pull requests and default-branch changes. CodeQL scans Python weekly, and Dependabot proposes weekly dependency and GitHub Actions updates. Pushing a version tag such as `v0.1.0` publishes a container image to GitHub Container Registry as `ghcr.io/<owner>/infera-engine`.

Run the same checks locally with `make check` (or the individual commands in `CONTRIBUTING.md`).

## Overview

Infera Engine is designed to analyze complex, rapidly changing topics by combining evidence from multiple sources into a structured reasoning pipeline.

Rather than producing a single answer from a language model, Infera decomposes the problem into specialized stages. Each stage contributes a well-defined output that is used by the next stage, resulting in forecasts that can be traced back to the supporting evidence.

The system is intended for analytical tasks such as policy analysis, geopolitical events, market intelligence, technology trends, and other domains where conclusions must be supported by verifiable information.

---

## Objectives

- Collect evidence from multiple sources
- Extract structured claims and entities
- Identify relationships between entities
- Detect conflicting information
- Evaluate multiple hypotheses
- Generate explainable future scenarios
- Produce transparent analytical reports

---

## Architecture

```
                    External Sources
                           │
                           ▼
                 Evidence Collection
                           │
                           ▼
                    Research Agent
                           │
                           ▼
                    Planner Agent
                           │
                           ▼
                Evidence Processing
                           │
                           ▼
                  Claim Extraction
                           │
                           ▼
                  Entity Extraction
                           │
                           ▼
               Knowledge Graph Builder
                           │
                           ▼
              Contradiction Detection
                           │
                           ▼
               Scenario Generation
                           │
                           ▼
                    Critic Agent
                           │
                           ▼
                  Intelligence Report
```

---

## Multi-Agent Workflow

Infera uses functional agents rather than simulated personas.

| Agent | Responsibility |
|-------|----------------|
| Research Agent | Collects relevant evidence |
| Planner Agent | Breaks the task into analytical steps |
| Claim Processor | Extracts factual claims |
| Entity Processor | Identifies entities and relationships |
| Knowledge Graph Builder | Organizes structured information |
| Contradiction Analyzer | Detects conflicting evidence |
| Scenario Generator | Produces plausible future outcomes |
| Critic Agent | Reviews assumptions and reasoning |
| Report Generator | Produces the final analytical report |

Each agent performs a single responsibility and communicates through structured state.

---

## Project Structure

```
Infera-Engine/

├── core/
│   ├── agents/
│   ├── nodes/
│   ├── tools/
│   ├── graph.py
│   ├── models.py
│   └── state.py
│
├── ui/
├── utils/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## Technology Stack

### Backend

- Python
- FastAPI

### Agent Orchestration

- LangGraph

### Language Models

- Groq API
- Llama 3

### Knowledge Representation

- NetworkX

### Frontend

- React
- TypeScript

---

## Current Capabilities

- Multi-agent reasoning workflow
- Evidence collection
- Search integration
- Task planning
- Scenario generation
- Critical review
- Structured reporting

---

## Planned Features

- Claim extraction
- Entity linking
- Knowledge graph visualization
- Narrative clustering
- Contradiction analysis
- Confidence estimation
- Interactive evidence explorer
- Timeline analysis
- Exportable analytical reports

---

## Design Principles

- Evidence before conclusions
- Independent functional agents
- Explainable reasoning
- Traceable outputs
- Modular architecture
- Deterministic processing where practical

---

## Disclaimer

Infera Engine is an analytical reasoning framework intended to assist investigation and decision support. Forecasts are generated from available evidence and should be interpreted as analytical scenarios rather than definitive predictions.

---

## License

MIT License
