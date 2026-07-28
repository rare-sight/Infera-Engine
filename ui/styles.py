def load_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        background-color: #0b0f14;
        color: #e6edf3;
    }

    .stApp {
        background-color: #0b0f14;
    }

    /* Header */
    .main-header {
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: -0.5px;
        color: #f0f6fc;
        margin-bottom: 0.2rem;
    }

    .sub-header {
        font-size: 0.9rem;
        color: #8b949e;
        margin-bottom: 1.5rem;
    }

    /* Cards */
    .infera-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #58a6ff;
        margin-bottom: 0.75rem;
    }

    .card-content {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #c9d1d9;
    }

    /* Status / Progress */
    .step-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
        font-size: 0.9rem;
        color: #8b949e;
    }

    .step-item.active {
        color: #58a6ff;
        font-weight: 500;
    }

    .step-item.done {
        color: #3fb950;
    }

    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #30363d;
        flex-shrink: 0;
    }

    .step-item.active .step-dot {
        background: #58a6ff;
        box-shadow: 0 0 8px #58a6ff;
    }

    .step-item.done .step-dot {
        background: #3fb950;
    }

    /* Input */
    .stTextInput > div > div > input {
        background-color: #0d1117;
        border: 1px solid #30363d;
        color: #e6edf3;
        border-radius: 6px;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(180deg, #1f6feb 0%, #1158c7 100%);
        color: white;
        border: 1px solid #1f6feb;
        border-radius: 6px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, #388bfd 0%, #1f6feb 100%);
        border-color: #388bfd;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #21262d;
    }

    /* Scenario probability badges */
    .prob-high { color: #f85149; font-weight: 600; }
    .prob-medium { color: #d29922; font-weight: 600; }
    .prob-low { color: #3fb950; font-weight: 600; }

    /* Divider */
    hr {
        border-color: #21262d;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """