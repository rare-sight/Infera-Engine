import streamlit as st


def render_header():
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div style="font-size: 1.5rem; font-weight: 600; letter-spacing: 1.5px; color: #e6edf3;">
            INFERA
        </div>
        <div style="font-size: 0.78rem; color: #8b949e; margin-top: 3px; letter-spacing: 0.5px;">
            MULTI-AGENT FORESIGHT SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_step_status(current_step: str):
    steps = [
        ("entity", "01 Entity"),
        ("research", "02 Research"),
        ("reconcile", "03 Reconcile"),
        ("analyze", "04 Analyst"),
        ("uncertainties", "05 Uncertainties"),
        ("scenarios", "06 Scenario+Critic"),
    ]
    order = ["entity", "research", "reconcile", "analyze", "uncertainties", "scenarios", "complete"]
    current_idx = order.index(current_step) if current_step in order else -1

    cols = st.columns(6)
    for i, (key, label) in enumerate(steps):
        with cols[i]:
            if i < current_idx:
                st.markdown(
                    f"<div style='color:#3fb950; font-size:0.72rem;'>{label} ✓</div>",
                    unsafe_allow_html=True,
                )
            elif i == current_idx:
                st.markdown(
                    f"<div style='color:#58a6ff; font-size:0.72rem; font-weight:500;'>{label} →</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='color:#484f58; font-size:0.72rem;'>{label}</div>",
                    unsafe_allow_html=True,
                )


def render_section(title: str, content: str):
    st.markdown(f"**{title}**")
    st.markdown(content)
    st.markdown("---")


def render_agent_log(message: str):
    st.markdown(f"<div style='color:#8b949e; font-size:0.85rem; margin-bottom:0.5rem;'>→ {message}</div>", unsafe_allow_html=True)