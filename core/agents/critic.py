from langchain_core.messages import HumanMessage
from core.models import get_groq_llm


def critique_scenarios(topic: str, scenarios_text: str, research: str) -> str:
    """Critic Agent (Red Team): Challenges and improves the scenarios."""
    llm = get_groq_llm()

    prompt = f"""You are a Red Team critic inside an intelligence unit.
Your job is to rigorously challenge the scenarios below.

Topic: {topic}

Research Brief:
{research}

Scenarios to critique:
{scenarios_text}

Instructions:
1. Point out weaknesses, assumptions, or blind spots in each scenario.
2. Suggest one concrete improvement for each scenario.
3. Then provide a short refined version of the strongest scenario.

Be direct and analytical.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content