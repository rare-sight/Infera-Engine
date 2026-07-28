from langchain_core.messages import HumanMessage
from core.models import get_local_llm
from core.state import InferaState


def identify_uncertainties(state: InferaState) -> dict:
    llm = get_local_llm()
    topic = state["topic"]
    analysis = state["analysis"]
    research = state["research"]

    prompt = f"""You are a senior intelligence analyst.
Your job is to extract the most decision-relevant uncertainties from the research provided.

Topic: {topic}

=== ANALYSIS ===
{analysis}

=== RESEARCH BRIEF (this is your main source) ===
{research}

Instructions:
- Base your uncertainties STRICTLY on the research above.
- Do not invent generic points.
- Each uncertainty must be specific and forward-looking (2–5 year horizon).
- Return exactly 5 uncertainties.
- Format as a clean numbered list. No extra commentary.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        "uncertainties": response.content,
        "current_step": "uncertainties_complete"
    }