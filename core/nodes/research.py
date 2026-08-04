from core.agents.planner import plan_research
from core.agents.researcher import run_research_agent
from core.agents.entity import entity_card_to_context
from core.state import InferaState


def research_topic(state: InferaState) -> dict:
    topic = state["topic"]

    entity_raw = state.get("entity_card") or {
        "name": topic,
        "entity_type": "other",
        "jurisdiction": "unknown",
        "role_or_context": "unknown",
        "disambiguation_note": "",
        "confidence": "low",
        "resolution_stage": "provisional",
    }
    entity_ctx = entity_card_to_context(entity_raw)

    planner_input = f"{topic}\n\n{entity_ctx}"
    questions = plan_research(planner_input)
    research_brief = run_research_agent(topic, questions)

    return {
        "research": research_brief,
        "current_step": "research_complete",
    }