import os

import streamlit as st
from dotenv import load_dotenv

from core.graph import build_infera_graph
from core.memory import save_run
from core.models import DEFAULT_GROQ_MODEL, configure_models
from ui.components import render_agent_log, render_header, render_section, render_step_status
from ui.styles import load_css

load_dotenv()

st.set_page_config(
    page_title="Infera",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(load_css(), unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ◆ INFERA")
    st.caption("Multi-Agent Foresight System")
    st.markdown("---")
    st.markdown("**Pipeline**")
    st.markdown("- Entity (provisional)")
    st.markdown("- Research")
    st.markdown("- Entity Reconcile")
    st.markdown("- Analyst")
    st.markdown("- Uncertainties")
    st.markdown("- Scenario + per-scenario Base Rate + Critic")
    st.markdown("---")
    st.caption("v0.6 • Grounded Forecasting")

    st.markdown("---")
    st.markdown("**Model settings**")
    model_options = {
        "GPT-OSS 120B (recommended)": "openai/gpt-oss-120b",
        "Llama 3.3 70B (requires Groq account access)": "llama-3.3-70b-versatile",
    }
    configured_model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
    default_label = next(
        (label for label, model_id in model_options.items() if model_id == configured_model),
        "GPT-OSS 120B (recommended)",
    )
    selected_label = st.selectbox(
        "Groq reasoning model",
        options=list(model_options),
        index=list(model_options).index(default_label),
        help="Llama 3.3 remains available only to Groq accounts with access to it.",
    )
    use_local_low_power = st.toggle(
        "Use local LLM for low-power tasks",
        help="Routes only analysis and uncertainty extraction to Ollama; all other stages stay on Groq.",
    )
    local_model = "qwen3:8b"
    if use_local_low_power:
        local_model = st.text_input("Local Ollama model", value=os.getenv("OLLAMA_MODEL", local_model))
        st.caption("Requires Ollama running at http://localhost:11434.")

# Main
render_header()

topic = st.text_input(
    "topic_input",
    placeholder="Enter developing topic...",
    label_visibility="collapsed",
)

run_btn = st.button("Run Analysis", type="primary")

if run_btn:
    if not topic.strip():
        st.warning("Enter a topic first.")
    elif not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY missing")
    else:
        configure_models(
            groq_model=model_options[selected_label],
            use_local_low_power=use_local_low_power,
            local_model=local_model,
        )
        graph = build_infera_graph()

        status_box = st.empty()
        log_box = st.empty()
        entity_box = st.empty()
        research_box = st.empty()
        reconcile_box = st.empty()
        analysis_box = st.empty()
        uncertainties_box = st.empty()
        scenarios_box = st.empty()

        state = {
            "topic": topic.strip(),
            "entity_card": None,
            "base_rate": None,
            "analysis": "",
            "research": "",
            "uncertainties": "",
            "scenarios_text": "",
            "structured_scenarios": None,
            "current_step": "entity",
        }

        try:
            # 1. Entity (provisional)
            with status_box.container():
                render_step_status("entity")
            with log_box.container():
                render_agent_log("Entity Resolver (provisional)...")
            result = graph.nodes["entity"].invoke(state)
            state.update(result)
            with entity_box.container():
                card = state.get("entity_card") or {}
                entity_text = (
                    f"**Name:** {card.get('name', 'N/A')}\n\n"
                    f"**Type:** {card.get('entity_type', 'N/A')}\n\n"
                    f"**Jurisdiction:** {card.get('jurisdiction', 'N/A')}\n\n"
                    f"**Role:** {card.get('role_or_context', 'N/A')}\n\n"
                    f"**Note:** {card.get('disambiguation_note', '')}\n\n"
                    f"**Confidence:** {card.get('confidence', 'N/A')}\n\n"
                    f"**Stage:** {card.get('resolution_stage', 'provisional')}"
                )
                render_section("ENTITY CARD (Provisional)", entity_text)

            # 2. Research
            with status_box.container():
                render_step_status("research")
            with log_box.container():
                render_agent_log("Research Agent is searching and synthesizing...")
            result = graph.nodes["research"].invoke(state)
            state.update(result)
            with research_box.container():
                render_section("RESEARCH BRIEF", state["research"])

            # 3. Entity Reconciliation
            with status_box.container():
                render_step_status("reconcile")
            with log_box.container():
                render_agent_log("Reconciling entity against research...")
            result = graph.nodes["reconcile"].invoke(state)
            state.update(result)
            with reconcile_box.container():
                card = state.get("entity_card") or {}
                entity_text = (
                    f"**Name:** {card.get('name', 'N/A')}\n\n"
                    f"**Type:** {card.get('entity_type', 'N/A')}\n\n"
                    f"**Jurisdiction:** {card.get('jurisdiction', 'N/A')}\n\n"
                    f"**Role:** {card.get('role_or_context', 'N/A')}\n\n"
                    f"**Note:** {card.get('disambiguation_note', '')}\n\n"
                    f"**Confidence:** {card.get('confidence', 'N/A')}\n\n"
                    f"**Stage:** {card.get('resolution_stage', 'reconciled')}"
                )
                render_section("ENTITY CARD (Reconciled)", entity_text)

            # 4. Analyst
            with status_box.container():
                render_step_status("analyze")
            with log_box.container():
                render_agent_log("Analyst Agent is assessing grounded research...")
            result = graph.nodes["analyze"].invoke(state)
            state.update(result)
            with analysis_box.container():
                render_section("ANALYSIS", state["analysis"])

            # 5. Uncertainties
            with status_box.container():
                render_step_status("uncertainties")
            with log_box.container():
                render_agent_log("Extracting key uncertainties...")
            result = graph.nodes["uncertainties"].invoke(state)
            state.update(result)
            with uncertainties_box.container():
                render_section("KEY UNCERTAINTIES", state["uncertainties"])

            # 6. Scenarios (includes per-scenario base rate + critic)
            with status_box.container():
                render_step_status("scenarios")
            with log_box.container():
                render_agent_log("Scenario Agent drafting forecasts...")
                render_agent_log("Computing per-scenario base rates + scores...")
                render_agent_log("Critic Agent challenging scenarios...")
            result = graph.nodes["scenarios"].invoke(state)
            state.update(result)
            with scenarios_box.container():
                render_section("SCENARIOS + RED TEAM CRITIQUE", state["scenarios_text"])

            # Save
            try:
                save_path = save_run(topic.strip(), state)
                st.caption(f"Saved to memory: `{save_path}`")
            except Exception:
                pass

            with status_box.container():
                render_step_status("complete")
            with log_box.container():
                render_agent_log("All agents completed.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
