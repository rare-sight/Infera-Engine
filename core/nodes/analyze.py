from langchain_core.messages import HumanMessage
from core.models import get_local_llm
from core.state import InferaState


def analyze_topic(state: InferaState) -> dict:
    llm = get_local_llm()
    topic = state["topic"]

    prompt = f"""You are a senior strategic foresight analyst.
Produce a concise, high-signal overview of the developing topic.

Topic: {topic}

Respond in this exact format:

Current Status:
<2-4 sentences>

Key Drivers:
- driver 1
- driver 2
- driver 3
- driver 4
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        "analysis": response.content,
        "current_step": "analysis_complete"
    }