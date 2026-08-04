from langchain_core.messages import HumanMessage
from core.models import get_groq_llm
from core.state import BaseRateEstimate
from core.agents.entity import entity_card_to_context


def estimate_base_rate_for_scenario(
    entity_card: dict,
    forecast_statement: str,
    time_horizon: str,
) -> BaseRateEstimate:
    """Per-scenario base rate, matched to THIS forecast's direction and scale."""
    llm = get_groq_llm()
    entity_ctx = entity_card_to_context(entity_card)

    prompt = f"""You are a base-rate forecasting specialist for ONE specific scenario.

{entity_ctx}

THIS SCENARIO'S FORECAST:
"{forecast_statement}"
Time horizon: {time_horizon}

RULES:
1. Match reference class DIRECTION to this forecast (success vs pushback/failure).
2. Match SCALE to the entity (state commissioner ≠ national PM / national agency).
3. Give estimated_base_rate_pct 0-100.
4. Name 1-3 comparable cases at similar scale, or say if none fit well.

Return structured BaseRateEstimate.
"""
    structured = llm.with_structured_output(BaseRateEstimate)
    return structured.invoke([HumanMessage(content=prompt)])