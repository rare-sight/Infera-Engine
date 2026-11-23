from core.models import get_groq_llm, invoke_structured_model
from core.state import EntityCard


def resolve_entity_provisional(topic: str) -> EntityCard:
    """Phase 1: resolve from topic string only. Mark as provisional."""
    llm = get_groq_llm()
    prompt = f"""You are an entity resolution specialist.

Topic: {topic}

CRITICAL RULE:
If the topic names a SPECIFIC PERSON plus a generic acronym (e.g. FDA),
resolve around the PERSON's actual affiliation, not the most famous meaning of the acronym.
Example: "Tukaram Munde FDA" should NOT default to US FDA.

Return:
- name
- entity_type (person | organization | policy | event | product | other)
- jurisdiction (country/state)
- role_or_context
- disambiguation_note (e.g. "Not the US FDA — verify against research")
- resolution_stage must be "provisional"

Return only a valid JSON object matching the EntityCard fields. Do not use Markdown.
"""
    card = invoke_structured_model(llm, EntityCard, prompt, max_output_tokens=350)
    card.resolution_stage = "provisional"
    return card


def reconcile_entity(provisional: dict, research_brief: str) -> EntityCard:
    """Phase 2: correct provisional card against grounded research."""
    llm = get_groq_llm()
    prompt = f"""You are reconciling a PROVISIONAL entity card against a REAL research brief.

PROVISIONAL CARD:
- Name: {provisional.get("name")}
- Type: {provisional.get("entity_type")}
- Jurisdiction: {provisional.get("jurisdiction")}
- Role: {provisional.get("role_or_context")}
- Note: {provisional.get("disambiguation_note")}

RESEARCH BRIEF (trust this over the provisional guess when they conflict):
{research_brief}

Rules:
1. If research contradicts jurisdiction/role/org, CORRECT the card to match research.
2. If research confirms it, keep the values.
3. Set resolution_stage to "reconciled".

Return only a valid JSON object matching the EntityCard fields. Do not use Markdown.
"""
    card = invoke_structured_model(llm, EntityCard, prompt, max_output_tokens=400)
    card.resolution_stage = "reconciled"
    return card


def entity_card_to_context(card) -> str:
    if isinstance(card, dict):
        card = EntityCard(**card)

    lines = [
        "ENTITY CARD (ground truth for this run):",
        f"- Name: {card.name}",
        f"- Type: {card.entity_type}",
        f"- Jurisdiction: {card.jurisdiction}",
        f"- Role: {card.role_or_context}",
        f"- Stage: {card.resolution_stage}",
    ]
    if card.disambiguation_note:
        lines.append(f"- IMPORTANT: {card.disambiguation_note}")
    if card.resolution_stage == "provisional":
        lines.append("- WARNING: provisional only — not yet verified against research.")
    return "\n".join(lines)
