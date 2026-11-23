from types import SimpleNamespace

import pytest

from core.agents import researcher


def _response(content: str, finish_reason: str = "stop") -> SimpleNamespace:
    return SimpleNamespace(
        content=content,
        response_metadata={"finish_reason": finish_reason},
    )


def test_research_synthesis_uses_larger_output_and_covers_all_questions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(researcher, "get_groq_llm", lambda: object())
    monkeypatch.setattr(
        researcher,
        "web_search",
        SimpleNamespace(invoke=lambda query: f"Evidence for {query}. Source: https://example.com"),
    )
    requests = []

    def invoke_model(llm, prompt: str, max_output_tokens: int):
        requests.append((prompt, max_output_tokens))
        return _response("Complete research brief with cited evidence.")

    monkeypatch.setattr(researcher, "invoke_model", invoke_model)

    result = researcher.run_research_agent("Example topic", ["Question one", "Question two"])

    assert "Complete research brief" in result
    assert len(requests) == 1
    assert requests[0][1] == 3000
    assert "Question one" in requests[0][0]
    assert "Question two" in requests[0][0]


def test_research_synthesis_retries_if_output_was_truncated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(researcher, "get_groq_llm", lambda: object())
    monkeypatch.setattr(
        researcher,
        "web_search",
        SimpleNamespace(invoke=lambda query: "Evidence and source URL."),
    )
    limits = iter([_response("Partial", "length"), _response("Complete")])
    output_limits = []

    def invoke_model(llm, prompt: str, max_output_tokens: int):
        output_limits.append(max_output_tokens)
        return next(limits)

    monkeypatch.setattr(researcher, "invoke_model", invoke_model)

    result = researcher.run_research_agent("Example topic", ["Question one"])

    assert result == "Complete"
    assert output_limits == [3000, 4000]


def test_research_fails_explicitly_when_all_searches_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(researcher, "get_groq_llm", lambda: object())

    def fail_search(query: str) -> str:
        raise TimeoutError("search timed out")

    monkeypatch.setattr(researcher, "web_search", SimpleNamespace(invoke=fail_search))

    with pytest.raises(RuntimeError, match="no usable results"):
        researcher.run_research_agent("Example topic", ["Question one"])
