from langchain_core.messages import HumanMessage
from core.models import get_local_llm
from core.state import InferaState, EntityCard
from core.agents.entity import entity_card_to_context


def analyze_topic(state: InferaState) -> dict:
    research = (state.get("research") or "").strip()
    if not research:
        raise ValueError(
            "Analyst called before Research. Fix graph order: "
            "Entity → Research → Reconcile → Analyst"
        )

    entity_raw = state.get("entity_card") or {}
    if entity_raw.get("resolution_stage") != "reconciled":
        raise ValueError(
            "Analyst requires a reconciled Entity Card. "
            "Run Entity Reconciliation after Research first."
        )

    llm = get_local_llm()
    entity_ctx = entity_card_to_context(entity_raw)

    prompt = f"""You are a strategic foresight analyst.

STRICT RULE:
Use ONLY the Research Brief and Entity Card below.
Do not introduce agencies, laws, countries, or programs not present in the research.

{entity_ctx}

RESEARCH BRIEF:
{research}

Topic: {state['topic']}

Respond in this format:

Current Status:
<2-4 sentences grounded in the research>

Key Drivers:
- driver 1
- driver 2
- driver 3
- driver 4
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        "analysis": response.content,
        "current_step": "analysis_complete",
    }