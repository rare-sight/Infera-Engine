import difflib
from langchain_core.messages import HumanMessage
from core.models import get_groq_llm
from core.agents.critic import critique_scenarios
from core.agents.entity import entity_card_to_context
from core.agents.base_rate import estimate_base_rate_for_scenario
from core.state import InferaState, ScenarioSet
from core.scoring import compute_score, score_to_label, adjust_for_base_rate


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

STRICT RULES:
- forecast_statement must NOT restate research facts. Infer second-order effects.
- time_horizon: 3-6mo | 6-12mo | 1-3yr
- Exactly 3 scenarios. At least one must be resistance/pushback/failure.
- Provide 3-6 evidence factors in score_components.factors.
- Do NOT assign probability_label or numeric score.

SCORING RULE (critical):
Each factor is relative to THIS scenario's own forecast_statement.
- supports_forecast=true if the factor makes THIS claim more likely
- supports_forecast=false if it makes THIS claim less likely
Example: "industry lobbying history"
  - for a SMOOTH REFORM scenario → supports_forecast=false
  - for a PUSHBACK scenario → supports_forecast=true
strength: strong | moderate | weak

Return structured ScenarioSet.
"""

    structured = llm.with_structured_output(ScenarioSet)
    draft = structured.invoke([HumanMessage(content=draft_prompt)])

    finalized = []
    text_parts = []

    for s in draft.scenarios:
        br = estimate_base_rate_for_scenario(
            entity_card=entity_card,
            forecast_statement=s.forecast_statement,
            time_horizon=s.time_horizon,
        )

        score = compute_score(s.score_components)
        label = score_to_label(score)
        label, note = adjust_for_base_rate(label, br.estimated_base_rate_pct)

        s.score = score
        s.probability_label = label
        s.probability_reason = (
            f"{s.probability_reason} "
            f"[Base rate {br.estimated_base_rate_pct}% — {br.reference_class}] {note}"
        ).strip()

        if is_near_duplicate(s.forecast_statement, research):
            s.probability_reason += " [Warning: may be too close to research.]"

        finalized.append(s)

        text_parts.append(f"**{s.scenario_name}**\n")
        text_parts.append(f"Time horizon: `{s.time_horizon}`\n")
        text_parts.append(f"Forecast: {s.forecast_statement}\n\n")
        text_parts.append(
            f"Probability: `{s.probability_label}` (score={s.score}) — {s.probability_reason}\n\n"
        )
        text_parts.append(f"**Inferred from:** {', '.join(s.inferred_from)}\n")
        text_parts.append(f"**Evidence for:** {', '.join(s.evidence_for)}\n")
        text_parts.append(f"**Evidence against:** {', '.join(s.evidence_against)}\n")

        factor_lines = []
        for f in s.score_components.factors:
            direction = "supports" if f.supports_forecast else "opposes"
            factor_lines.append(f"{f.factor} ({direction}, {f.strength})")
        text_parts.append(f"**Factors:** {'; '.join(factor_lines)}\n")
        text_parts.append(
            f"**Comparable cases:** {', '.join(br.comparable_cases or [])}\n"
        )
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