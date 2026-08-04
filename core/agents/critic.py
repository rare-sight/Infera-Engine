from langchain_core.messages import HumanMessage
from core.models import get_groq_llm


def critique_scenarios(topic: str, scenarios_text: str, research: str) -> str:
    """
    Red Team critic — qualitative only.
    Must NOT assign High/Medium/Low or numeric scores.
    """
    llm = get_groq_llm()

    prompt = f"""You are a Red Team critic reviewing forecasting scenarios.

Topic: {topic}

Research Brief:
{research}

Scenarios:
{scenarios_text}

For EACH scenario provide:
1. Weaknesses / shaky assumptions
2. Blind spots
3. One concrete improvement suggestion

Then propose one refined strongest scenario as plain analysis:
- what should change in the forecast
- what evidence factors should be weighted differently
- refinement rationale

STRICT RULE:
Do NOT write probability labels (High/Medium/Low), percentages, or scores.
Those are computed only by the scoring pipeline, not by you.
If you want to express confidence, describe the evidence factors instead.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content