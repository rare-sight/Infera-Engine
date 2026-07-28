from langgraph.graph import StateGraph, START, END
from core.state import InferaState
from core.nodes import (
    analyze_topic,
    research_topic,
    identify_uncertainties,
    generate_scenarios,
)


def build_infera_graph():
    builder = StateGraph(InferaState)

    builder.add_node("analyze", analyze_topic)
    builder.add_node("research", research_topic)
    builder.add_node("uncertainties", identify_uncertainties)
    builder.add_node("scenarios", generate_scenarios)

    builder.add_edge(START, "analyze")
    builder.add_edge("analyze", "research")
    builder.add_edge("research", "uncertainties")
    builder.add_edge("uncertainties", "scenarios")
    builder.add_edge("scenarios", END)

    return builder.compile()