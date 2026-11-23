from core.tools import search


def test_web_search_falls_back_to_available_providers(monkeypatch) -> None:
    calls = []

    class FakeDDGS:
        def __init__(self, timeout):
            assert timeout == 12

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def text(self, query, max_results, backend):
            calls.append(backend)
            if backend == "google,bing":
                raise RuntimeError("combined provider failure")
            return [
                {
                    "title": "Official update",
                    "body": "Scheme installation progress",
                    "href": "https://example.com/update",
                }
            ]

    monkeypatch.setattr(search, "DDGS", FakeDDGS)

    result = search.web_search.invoke("PM Surya Ghar progress")

    assert calls == ["google,bing", "bing"]
    assert "Official update" in result
    assert "https://example.com/update" in result


def test_web_search_reports_all_provider_failures(monkeypatch) -> None:
    calls = []

    class FakeDDGS:
        def __init__(self, timeout):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def text(self, query, max_results, backend):
            calls.append((query, backend))
            raise RuntimeError(f"{backend} unavailable")

    monkeypatch.setattr(search, "DDGS", FakeDDGS)

    try:
        search.web_search.invoke("PM Surya Ghar progress")
    except RuntimeError as error:
        assert "google,bing" in str(error)
        assert "bing unavailable" in str(error)
        assert "yandex unavailable" in str(error)
        assert len(calls) == 3
    else:
        raise AssertionError("Expected provider failures to be surfaced.")


def test_web_search_retries_with_concise_query(monkeypatch) -> None:
    calls = []

    class FakeDDGS:
        def __init__(self, timeout):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def text(self, query, max_results, backend):
            calls.append((query, backend))
            if len(calls) < 4:
                return []
            return [
                {
                    "title": "Scheme progress",
                    "body": "Installed capacity update",
                    "href": "https://example.com/progress",
                }
            ]

    monkeypatch.setattr(search, "DDGS", FakeDDGS)
    long_query = (
        "How has adoption rate of PM Surya Ghar rooftop solar scheme progressed "
        "since launch and what quantitative indicators show beneficiaries?"
    )

    result = search.web_search.invoke(long_query)

    assert calls[:3] == [
        (long_query, "google,bing"),
        (long_query, "bing"),
        (long_query, "yandex"),
    ]
    assert (
        calls[3][0]
        == "adoption rate PM Surya Ghar rooftop solar scheme progressed launch quantitative indicators show beneficiaries"
    )
    assert "Scheme progress" in result
