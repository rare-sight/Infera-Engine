from langchain_core.messages import HumanMessage
from core.models import get_groq_llm


def plan_research(topic: str) -> list[str]:
    """Planner Agent: Decides the key research questions."""
    llm = get_groq_llm()

    prompt = f"""You are a senior intelligence planner.
Break down the following developing topic into 3 focused research questions that will help generate high-quality future scenarios.

Topic: {topic}

Return only the 3 questions, one per line. Make them specific and investigative.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    questions = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    return questions[:3]