import os
from contextvars import ContextVar

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
_groq_model: ContextVar[str] = ContextVar("groq_model", default=DEFAULT_GROQ_MODEL)
_use_local_low_power: ContextVar[bool] = ContextVar("use_local_low_power", default=False)
_local_model: ContextVar[str] = ContextVar("local_model", default="qwen3:8b")


def configure_models(
    groq_model: str = DEFAULT_GROQ_MODEL,
    use_local_low_power: bool = False,
    local_model: str = "qwen3:8b",
) -> None:
    """Configure model routing for the current Streamlit run."""
    _groq_model.set(groq_model)
    _use_local_low_power.set(use_local_low_power)
    _local_model.set(local_model)


def get_groq_llm() -> ChatGroq:
    """Return the Groq model selected for the current run."""
    return ChatGroq(
        model=_groq_model.get(),
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )


def get_low_power_llm():
    """Use Ollama only for the lower-cost stages when the user enables it."""
    if not _use_local_low_power.get():
        return get_groq_llm()

    return ChatOllama(
        model=_local_model.get(),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3,
    )
