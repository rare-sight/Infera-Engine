from core.models import get_groq_llm, invoke_model


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
Do NOT assess confidence or assign probabilities, percentages, or scores.
"""

    response = invoke_model(
        llm,
        prompt,
        max_output_tokens=700,
    )
    return response.content
