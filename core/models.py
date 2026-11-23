import json
import os
from collections import deque
from contextvars import ContextVar
from math import ceil
from threading import Lock
from time import monotonic, sleep

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, ValidationError

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_TPM_LIMIT = 8000
GROQ_TPM_HEADROOM = 100
GROQ_TPM_BUDGET = GROQ_TPM_LIMIT - GROQ_TPM_HEADROOM
GROQ_TOKEN_WINDOW_SECONDS = 60
_groq_model: ContextVar[str] = ContextVar("groq_model", default=DEFAULT_GROQ_MODEL)
_use_local_low_power: ContextVar[bool] = ContextVar("use_local_low_power", default=False)
_local_model: ContextVar[str] = ContextVar("local_model", default="qwen3:8b")
_groq_call_lock = Lock()
_groq_token_usage: deque[list[float | int]] = deque()
_groq_reserved_tokens = 0


def _response_token_usage(response) -> int | None:
    usage = getattr(response, "usage_metadata", None)
    if not isinstance(usage, dict):
        metadata = getattr(response, "response_metadata", None)
        usage = metadata.get("token_usage") if isinstance(metadata, dict) else None
    if not isinstance(usage, dict):
        return None

    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    total_tokens = usage.get("total_tokens")
    if isinstance(input_tokens, int) and isinstance(output_tokens, int):
        return input_tokens + output_tokens
    if isinstance(total_tokens, int):
        return total_tokens
    return None


def _invoke_groq(
    llm: ChatGroq,
    prompt: str,
    max_output_tokens: int,
):
    global _groq_reserved_tokens

    estimated_prompt_tokens = ceil(len(prompt.encode("utf-8")) / 3)
    available_output_tokens = GROQ_TPM_BUDGET - estimated_prompt_tokens - 64
    if available_output_tokens < 1:
        estimated_tokens = estimated_prompt_tokens + 64
        raise ValueError(
            f"Groq prompt is estimated at {estimated_tokens} tokens before output, "
            f"above the safe per-request budget of {GROQ_TPM_BUDGET}. Shorten the prompt."
        )
    bounded_output_tokens = min(max_output_tokens, available_output_tokens)
    reserved_tokens = estimated_prompt_tokens + bounded_output_tokens + 64

    with _groq_call_lock:
        while True:
            now = monotonic()
            while _groq_token_usage and now - _groq_token_usage[0][0] >= GROQ_TOKEN_WINDOW_SECONDS:
                _, expired_tokens = _groq_token_usage.popleft()
                _groq_reserved_tokens -= int(expired_tokens)

            if _groq_reserved_tokens + reserved_tokens <= GROQ_TPM_BUDGET:
                reservation: list[float | int] = [now, reserved_tokens]
                _groq_token_usage.append(reservation)
                _groq_reserved_tokens += reserved_tokens
                break

            wait_seconds = _groq_token_usage[0][0] + GROQ_TOKEN_WINDOW_SECONDS - now
            sleep(max(wait_seconds, 0))

        response = llm.bind(max_tokens=bounded_output_tokens).invoke([HumanMessage(content=prompt)])
        actual_tokens = _response_token_usage(response)
        if actual_tokens is not None:
            _groq_reserved_tokens += actual_tokens - reserved_tokens
            reservation[1] = actual_tokens
        return response


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
    options = {
        "model": _groq_model.get(),
        "temperature": 0.2,
        "api_key": os.getenv("GROQ_API_KEY"),
        "request_timeout": 120,
        "max_retries": 2,
    }
    if _groq_model.get().startswith("openai/gpt-oss-"):
        options["reasoning_effort"] = "low"
    return ChatGroq(**options)


def invoke_model(
    llm,
    prompt: str,
    max_output_tokens: int,
):
    """Invoke a model while keeping Groq usage under the rolling token budget."""
    if isinstance(llm, ChatGroq):
        return _invoke_groq(llm, prompt, max_output_tokens)
    return llm.bind(num_predict=max_output_tokens).invoke([HumanMessage(content=prompt)])


def invoke_structured_model(
    llm: ChatGroq,
    schema: type[BaseModel],
    prompt: str,
    max_output_tokens: int,
):
    schema_json = json.dumps(schema.model_json_schema(), separators=(",", ":"))
    request = (
        f"{prompt}\n\nReturn exactly one JSON object matching this schema. "
        "Do not include Markdown or surrounding prose.\n"
        f"JSON schema: {schema_json}"
    )

    attempt_output_tokens = max_output_tokens
    for attempt in range(2):
        response = _invoke_groq(llm, request, attempt_output_tokens)
        content = response.content
        if isinstance(content, list):
            content = "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )

        try:
            text = str(content).strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[-1]
                if text.endswith("```"):
                    text = text[:-3].strip()

            try:
                data = json.loads(text)
            except json.JSONDecodeError as parse_error:
                decoder = json.JSONDecoder()
                start = text.find("{")
                if start < 0:
                    raise ValueError("Model response did not contain a JSON object.")
                if start == 0:
                    raise parse_error
                data, _ = decoder.raw_decode(text[start:])

            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError, ValueError) as error:
            if attempt == 1:
                finish_reason = response.response_metadata.get("finish_reason")
                response_excerpt = str(content)[:500] or "<empty response>"
                raise ValueError(
                    f"{schema.__name__} response was not valid JSON matching its "
                    f"schema after 2 attempts. Last parse error: {error}. "
                    f"Finish reason: {finish_reason or 'unknown'}. "
                    f"Response excerpt: {response_excerpt}"
                ) from error

            request = (
                "The previous response was invalid"
                + (
                    " and was truncated at the output limit."
                    if response.response_metadata.get("finish_reason") == "length"
                    else "."
                )
                + " Return one complete valid JSON object matching the schema. "
                "Do not include Markdown or prose.\n"
                f"Validation error: {str(error)[:1000]}\n"
                f"Original task: {prompt[:1800]}\n"
                f"JSON schema: {schema_json}"
            )
            if response.response_metadata.get("finish_reason") == "length":
                attempt_output_tokens = max_output_tokens + 400

    raise RuntimeError("Structured response attempts ended unexpectedly.")


def get_low_power_llm():
    """Use Ollama only for the lower-cost stages when the user enables it."""
    if not _use_local_low_power.get():
        return get_groq_llm()

    return ChatOllama(
        model=_local_model.get(),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3,
    )
