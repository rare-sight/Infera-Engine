from core.agents.entity import resolve_entity_provisional
from core.state import InferaState


def entity_node(state: InferaState) -> dict:
    card = resolve_entity_provisional(state["topic"])
    return {
        "entity_card": card.model_dump(),
        "current_step": "entity_provisional",
    }