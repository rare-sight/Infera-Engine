from langgraph.graph import StateGraph, START, END
from core.state import InferaState

from core.nodes.entity_node import entity_node
from core.nodes.research import research_topic
from core.nodes.reconcile_node import reconcile_node
from core.nodes.analyze import analyze_topic
from core.nodes.uncertainties import identify_uncertainties
from core.nodes.scenarios import generate_scenarios


def build_infera_graph():
    builder = StateGraph(InferaState)

    builder.add_node("entity", entity_node)
    builder.add_node("research", research_topic)
    builder.add_node("reconcile", reconcile_node)
    builder.add_node("analyze", analyze_topic)
    builder.add_node("uncertainties", identify_uncertainties)
    builder.add_node("scenarios", generate_scenarios)

    builder.add_edge(START, "entity")
    builder.add_edge("entity", "research")
    builder.add_edge("research", "reconcile")
    builder.add_edge("reconcile", "analyze")
    builder.add_edge("analyze", "uncertainties")
    builder.add_edge("uncertainties", "scenarios")
    builder.add_edge("scenarios", END)

    return builder.compile()