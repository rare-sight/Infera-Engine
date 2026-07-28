import os
import streamlit as st
from dotenv import load_dotenv

from core.graph import build_infera_graph
from ui.styles import load_css
from ui.components import render_header, render_step_status, render_section, render_agent_log

load_dotenv()

st.set_page_config(
    page_title="Infera",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(load_css(), unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ◆ INFERA")
    st.caption("Multi-Agent Foresight System")
    st.markdown("---")
    st.markdown("**Agents**")
    st.markdown("- Planner Agent")
    st.markdown("- Research Agent (tool-using)")
    st.markdown("- Analyst Agent")
    st.markdown("- Scenario Agent")
    st.markdown("- Critic Agent (Red Team)")
    st.markdown("---")
    st.caption("v0.3 • Agentic")

# Main
render_header()

topic = st.text_input(
    "topic_input",
    placeholder="Enter developing topic...",
    label_visibility="collapsed"
)

run_btn = st.button("Run Analysis", type="primary")

if run_btn:
    if not topic.strip():
        st.warning("Enter a topic first.")
    elif not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY missing")
    else:
        graph = build_infera_graph()

        status_box = st.empty()
        log_box = st.empty()
        analysis_box = st.empty()
        research_box = st.empty()
        uncertainties_box = st.empty()
        scenarios_box = st.empty()

        state = {
            "topic": topic.strip(),
            "analysis": "",
            "research": "",
            "uncertainties": "",
            "scenarios_text": "",
            "structured_scenarios": None,
            "current_step": "analyze"
        }

        try:
            # 1. Analyst
            with status_box.container():
                render_step_status("analyze")
            with log_box.container():
                render_agent_log("Analyst Agent is assessing the topic...")
            result = graph.nodes["analyze"].invoke(state)
            state.update(result)
            with analysis_box.container():
                render_section("ANALYSIS", state["analysis"])

            # 2. Research Agent (Planner + iterative search)
            with status_box.container():
                render_step_status("research")
            with log_box.container():
                render_agent_log("Planner Agent is generating research questions...")
                render_agent_log("Research Agent is searching and synthesizing...")
            result = graph.nodes["research"].invoke(state)
            state.update(result)
            with research_box.container():
                render_section("RESEARCH BRIEF", state["research"])

            # 3. Uncertainties
            with status_box.container():
                render_step_status("uncertainties")
            with log_box.container():
                render_agent_log("Extracting key uncertainties...")
            result = graph.nodes["uncertainties"].invoke(state)
            state.update(result)
            with uncertainties_box.container():
                render_section("KEY UNCERTAINTIES", state["uncertainties"])

            # 4. Scenario + Critic
            with status_box.container():
                render_step_status("scenarios")
            with log_box.container():
                render_agent_log("Scenario Agent is generating futures...")
                render_agent_log("Critic Agent (Red Team) is challenging the scenarios...")
            result = graph.nodes["scenarios"].invoke(state)
            state.update(result)
            with scenarios_box.container():
                render_section("SCENARIOS + RED TEAM CRITIQUE", state["scenarios_text"])

            with status_box.container():
                render_step_status("complete")
            with log_box.container():
                render_agent_log("All agents completed.")

        except Exception as e:
            st.error(f"Error: {str(e)}")