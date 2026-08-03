from langchain_core.messages import HumanMessage
from core.models import get_groq_llm
from core.agents.critic import critique_scenarios
from core.state import InferaState, ScenarioSet


def generate_scenarios(state: InferaState) -> dict:
    llm = get_groq_llm()
    topic = state["topic"]
    analysis = state["analysis"]
    research = state["research"]
    uncertainties = state["uncertainties"]

    # --- Scenario Generation ---
    prompt = f"""You are a professional scenario planner in a strategic intelligence unit.
Create exactly 3 distinct, non-overlapping scenarios for the next 3–5 years.

Topic: {topic}

Analysis:
{analysis}

Research Brief:
{research}

Key Uncertainties:
{uncertainties}

### Probability Rules (follow strictly):
- **High**: Strong current evidence, clear momentum, and few major barriers.
- **Medium**: Plausible and supported by some evidence, but depends on unresolved uncertainties.
- **Low**: Possible, but requires significant change or faces strong resistance.

For each scenario provide:
- name (short, evocative, do not start with "Scenario")
- description (4–6 concrete sentences)
- probability (High / Medium / Low)
- probability_reason (1 short sentence explaining why this probability was chosen)
- key_drivers (3–5 items)
- early_signals (3–4 observable indicators)

Make the three scenarios clearly different from each other.
"""

    structured_llm = llm.with_structured_output(ScenarioSet)
    result = structured_llm.invoke([HumanMessage(content=prompt)])

    # Build readable text
    text_parts = []
    for i, s in enumerate(result.scenarios, 1):
       text_parts.append(f"**{s.name}**\n")
    text_parts.append(f"Probability: `{s.probability}` — {s.probability_reason}\n\n")
    text_parts.append(f"{s.description}\n\n")
    text_parts.append(f"**Key Drivers:** {', '.join(s.key_drivers)}\n\n")
    text_parts.append(f"**Early Signals:** {', '.join(s.early_signals)}\n")

    scenarios_text = "".join(text_parts)
from langchain_core.messages import HumanMessage
from core.models import get_groq_llm
from core.agents.critic import critique_scenarios
from core.state import InferaState, ScenarioSet


def generate_scenarios(state: InferaState) -> dict:
    llm = get_groq_llm()
    topic = state["topic"]
    analysis = state["analysis"]
    research = state["research"]
    uncertainties = state["uncertainties"]

    prompt = f"""You are a professional scenario planner in a strategic intelligence unit.
Create exactly 3 distinct, non-overlapping scenarios for the next 3–5 years.

Topic: {topic}

Analysis:
{analysis}

Research Brief:
{research}

Key Uncertainties:
{uncertainties}

### Probability Rules (follow strictly):
- High: Strong current evidence, clear momentum, and few major barriers.
- Medium: Plausible and supported by some evidence, but depends on unresolved uncertainties.
- Low: Possible, but requires significant change or faces strong resistance.

For each scenario provide:
- name (short, evocative, do NOT start with "Scenario")
- description (4–6 concrete sentences)
- probability (High / Medium / Low)
- probability_reason (1 short sentence explaining why this probability was chosen)
- key_drivers (3–5 items)
- early_signals (3–4 observable indicators)

Make the three scenarios clearly different from each other.
"""

    structured_llm = llm.with_structured_output(ScenarioSet)
    result = structured_llm.invoke([HumanMessage(content=prompt)])

    text_parts = []
    for i, s in enumerate(result.scenarios, 1):
        text_parts.append(f"**{s.name}**\n")
        text_parts.append(f"Probability: `{s.probability}` — {s.probability_reason}\n\n")
        text_parts.append(f"{s.description}\n\n")
        text_parts.append(f"**Key Drivers:** {', '.join(s.key_drivers)}\n\n")
        text_parts.append(f"**Early Signals:** {', '.join(s.early_signals)}\n")
        if i < len(result.scenarios):
            text_parts.append("\n---\n\n")

    scenarios_text = "".join(text_parts)

    # Red Team critique
    critique = critique_scenarios(topic, scenarios_text, research)
    full_output = scenarios_text + "\n\n### Red Team Critique\n\n" + critique

    return {
        "structured_scenarios": result.model_dump(),
        "scenarios_text": full_output,
        "current_step": "complete"
    }
    # --- Critic Agent (Red Team) ---
    critique = critique_scenarios(topic, scenarios_text, research)

    full_output = scenarios_text + "\n\n### Red Team Critique\n\n" + critique

    return {
        "structured_scenarios": result.model_dump(),
        "scenarios_text": full_output,
        "current_step": "complete"
    }