import re

from ddgs import DDGS
from langchain_core.tools import tool


_SEARCH_STOP_WORDS = {
    "a",
    "about",
    "after",
    "and",
    "are",
    "as",
    "at",
    "by",
    "do",
    "for",
    "from",
    "has",
    "have",
    "how",
    "in",
    "into",
    "is",
    "its",
    "of",
    "on",
    "or",
    "since",
    "such",
    "that",
    "the",
    "their",
    "this",
    "to",
    "under",
    "what",
    "when",
    "which",
    "who",
    "why",
    "with",
}


def _search_query_variants(query: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", query)
    concise_query = " ".join(word for word in words if word.lower() not in _SEARCH_STOP_WORDS)
    concise_query = " ".join(concise_query.split()[:16])
    variants = [query.strip()]
    if concise_query and concise_query.casefold() != query.strip().casefold():
        variants.append(concise_query)
    return variants


@tool
def web_search(query: str) -> str:
    """Search the web for recent and relevant information."""
    errors = []
    results = []
    for query_variant in _search_query_variants(query):
        for backend in ("google,bing", "bing", "yandex"):
            try:
                with DDGS(timeout=12) as ddgs:
                    results = list(ddgs.text(query_variant, max_results=6, backend=backend))
            except Exception as error:
                errors.append(f"{backend}: {error}")
                continue
            if results:
                break
            errors.append(f"{backend}: no results for query variant")
        if results:
            break

    if not results:
        detail = "; ".join(errors)
        raise RuntimeError(f"No web search provider returned results. {detail}")

    output = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")[:160]
        body = r.get("body", "")[:500]
        href = r.get("href", "")[:240]
        output.append(f"{i}. {title}\n{body}\nSource: {href}\n")
    return "\n".join(output)
