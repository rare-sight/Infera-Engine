from core.agents.base_rate import estimate_base_rate
from core.state import InferaState


def base_rate_node(state: InferaState) -> dict:
    estimate = estimate_base_rate(
        topic=state["topic"],
        entity_card=state.get("entity_card") or {},
        research=state.get("research") or "",
    )
    return {
        "base_rate": estimate.model_dump(),
        "current_step": "base_rate_complete",
    }