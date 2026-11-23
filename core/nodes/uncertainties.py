from core.models import get_low_power_llm, invoke_model
from core.state import InferaState


def identify_uncertainties(state: InferaState) -> dict:
    llm = get_low_power_llm()
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

    response = invoke_model(
        llm,
        prompt,
        max_output_tokens=350,
    )
    return {"uncertainties": response.content, "current_step": "uncertainties_complete"}
