from core.models import get_groq_llm, invoke_model


def plan_research(topic: str) -> list[str]:
    """Use a model to select focused, topic-specific research questions."""
    prompt = f"""Break this topic into 3 focused investigative research questions.
Cover recent developments, key actors and decisions, and evidence about outcomes or risks.
Return only the questions, one per line.

Topic: {topic}
"""
    response = invoke_model(get_groq_llm(), prompt, max_output_tokens=220)
    questions = [line.strip("- •\t ") for line in response.content.splitlines()]
    questions = [question for question in questions if question]
    if not questions:
        raise ValueError("Research planner returned no questions.")
    return questions[:3]
