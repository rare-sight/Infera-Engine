from core.agents.entity import reconcile_entity
from core.state import InferaState


def reconcile_node(state: InferaState) -> dict:
    provisional = state.get("entity_card") or {}
    research = state.get("research") or ""
    card = reconcile_entity(provisional, research)
    return {
        "entity_card": card.model_dump(),
        "current_step": "entity_reconciled",
    }