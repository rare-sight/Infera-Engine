from core.agents.planner import plan_research
from core.agents.researcher import run_research_agent
from core.state import InferaState


def research_topic(state: InferaState) -> dict:
    topic = state["topic"]

    # 1. Planner Agent decides what to research
    questions = plan_research(topic)

    # 2. Research Agent runs iterative search + synthesis
    research_brief = run_research_agent(topic, questions)

    return {
        "research": research_brief,
        "current_step": "research_complete"
    }