import difflib

from core.agents.critic import critique_scenarios
from core.agents.entity import entity_card_to_context
from core.models import get_groq_llm, invoke_structured_model
from core.state import InferaState, ScenarioSet


def is_near_duplicate(forecast: str, research: str, threshold: float = 0.75) -> bool:
    sentences = [s.strip() for s in research.split(".") if s.strip()]
    for s in sentences:
        if difflib.SequenceMatcher(None, forecast.lower(), s.lower()).ratio() >= threshold:
            return True
    return False


def generate_scenarios(state: InferaState) -> dict:
    llm = get_groq_llm()
    topic = state["topic"]
    research = state.get("research") or ""
    entity_card = state.get("entity_card") or {}
    entity_ctx = entity_card_to_context(entity_card)

    draft_prompt = f"""You are a forecasting analyst. Produce genuine forecasts, not summaries.

{entity_ctx}

RESEARCH BRIEF:
{research}

Generate exactly 3 substantive forward-looking scenarios, including one resistance
or failure case. Use only research facts, with forecasts that infer rather than
restate. Use horizons 3-6mo, 6-12mo, or 1-3yr. For each scenario, provide 3-6
evidence factors, explain each factor, and include relevant evidence for and against
the forecast. Include up to 5 items in inferred_from, evidence_for, and
evidence_against. Do not assign overall confidence or probability.

EVIDENCE FACTOR RULE:
Each factor is relative to THIS scenario's own forecast_statement.
- supports_forecast=true if the factor makes THIS claim more likely
- supports_forecast=false if it makes THIS claim less likely
Example: "industry lobbying history"
  - for a SMOOTH REFORM scenario → supports_forecast=false
  - for a PUSHBACK scenario → supports_forecast=true
strength describes the evidence factor only: strong | moderate | weak

Return only a valid JSON object matching the ScenarioSet fields. Do not use Markdown.
"""

    draft = invoke_structured_model(
        llm,
        ScenarioSet,
        draft_prompt,
        max_output_tokens=3000,
    )

    finalized = []
    text_parts = []

    for s in draft.scenarios:
        if is_near_duplicate(s.forecast_statement, research):
            forecast_warning = " [Warning: may be too close to research.]"
        else:
            forecast_warning = ""

        finalized.append(s)

        text_parts.append(f"**{s.scenario_name}**\n")
        text_parts.append(f"Time horizon: `{s.time_horizon}`\n")
        text_parts.append(f"Forecast: {s.forecast_statement}{forecast_warning}\n\n")
        text_parts.append(f"**Inferred from:** {', '.join(s.inferred_from)}\n")
        text_parts.append(f"**Evidence for:** {', '.join(s.evidence_for)}\n")
        text_parts.append(f"**Evidence against:** {', '.join(s.evidence_against)}\n")

        factor_lines = []
        for f in s.score_components.factors:
            direction = "supports" if f.supports_forecast else "opposes"
            factor_lines.append(f"{f.factor} ({direction}, {f.strength})")
        text_parts.append(f"**Factors:** {'; '.join(factor_lines)}\n")
        text_parts.append("\n---\n\n")

    scenarios_text = "".join(text_parts)

    # Critic: qualitative only — must NOT invent probability labels
    critique = critique_scenarios(topic, scenarios_text, research)
    full_output = scenarios_text + "\n\n### Red Team Critique\n\n" + critique

    return {
        "structured_scenarios": {"scenarios": [x.model_dump() for x in finalized]},
        "scenarios_text": full_output,
        "current_step": "complete",
    }
