from collections import deque
from math import ceil
from types import SimpleNamespace

import pytest

from core import models


@pytest.fixture(autouse=True)
def reset_groq_usage(monkeypatch) -> None:
    monkeypatch.setattr(models, "_groq_token_usage", deque())
    monkeypatch.setattr(models, "_groq_reserved_tokens", 0)


def test_groq_output_limit_is_reduced_to_fit_request_budget(monkeypatch) -> None:
    captured = {}

    class FakeGroq:
        def bind(self, **kwargs):
            captured.update(kwargs)
            return self

        def invoke(self, messages):
            return SimpleNamespace(content="ok")

    prompt = "x" * 12_000

    models._invoke_groq(FakeGroq(), prompt, max_output_tokens=4000)

    expected_output_limit = models.GROQ_TPM_BUDGET - ceil(len(prompt.encode("utf-8")) / 3) - 64
    assert captured["max_tokens"] == expected_output_limit
    assert models._groq_reserved_tokens == (
        ceil(len(prompt.encode("utf-8")) / 3) + expected_output_limit + 64
    )
    assert (
        ceil(len(prompt.encode("utf-8")) / 3) + captured["max_tokens"] + 64
        <= models.GROQ_TPM_BUDGET
        < models.GROQ_TPM_LIMIT
    )


def test_groq_output_limit_remains_unchanged_when_it_fits(monkeypatch) -> None:
    captured = {}

    class FakeGroq:
        def bind(self, **kwargs):
            captured.update(kwargs)
            return self

        def invoke(self, messages):
            return SimpleNamespace(content="ok")

    models._invoke_groq(FakeGroq(), "short prompt", max_output_tokens=1200)

    assert captured["max_tokens"] == 1200


def test_groq_call_waits_only_when_the_rolling_budget_is_exhausted(
    monkeypatch,
) -> None:
    now = [100.0]
    waits = []

    def fake_sleep(seconds: float) -> None:
        waits.append(seconds)
        now[0] += seconds

    class FakeGroq:
        def bind(self, **kwargs):
            return self

        def invoke(self, messages):
            return SimpleNamespace(content="ok")

    monkeypatch.setattr(models, "monotonic", lambda: now[0])
    monkeypatch.setattr(models, "sleep", fake_sleep)
    llm = FakeGroq()

    models._invoke_groq(llm, "a" * 9000, max_output_tokens=3000)
    assert waits == []

    models._invoke_groq(llm, "b" * 3000, max_output_tokens=1000)

    assert waits == [models.GROQ_TOKEN_WINDOW_SECONDS]
    assert models._groq_reserved_tokens == 2064


def test_actual_usage_releases_unused_output_reservation(monkeypatch) -> None:
    now = [10.0]
    waits = []

    def fake_sleep(seconds: float) -> None:
        waits.append(seconds)
        now[0] += seconds

    class FakeGroq:
        def bind(self, **kwargs):
            return self

        def invoke(self, messages):
            return SimpleNamespace(
                content="ok",
                usage_metadata={"input_tokens": 10, "output_tokens": 20},
            )

    monkeypatch.setattr(models, "monotonic", lambda: now[0])
    monkeypatch.setattr(models, "sleep", fake_sleep)
    llm = FakeGroq()

    models._invoke_groq(llm, "first", max_output_tokens=6000)
    assert models._groq_reserved_tokens == 30

    models._invoke_groq(llm, "second", max_output_tokens=1800)

    assert waits == []
    assert models._groq_reserved_tokens == 60


def test_groq_prompt_that_exceeds_budget_fails_explicitly() -> None:
    prompt = "x" * (models.GROQ_TPM_BUDGET * 3)

    with pytest.raises(ValueError, match="Shorten the prompt"):
        models._invoke_groq(object(), prompt, max_output_tokens=100)
