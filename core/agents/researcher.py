from math import ceil

from core.models import GROQ_TPM_BUDGET, get_groq_llm, invoke_model
from core.tools.search import web_search


def run_research_agent(topic: str, questions: list[str]) -> str:
    llm = get_groq_llm()
    collected_info = []
    search_failures = []

    for question in questions:
        search_query = f"{topic} {question}"
        try:
            search_result = web_search.invoke(search_query)
        except Exception as error:
            search_failures.append(f"{question}: {error}")
            continue

        if search_result == "No results found.":
            search_failures.append(f"{question}: no search results")
            continue

        collected_info.append(
            f"### Research Question\n{question}\n\n### Search Results\n{search_result}\n"
        )

    if not collected_info:
        details = "; ".join(search_failures) or "No research questions were provided."
        raise RuntimeError(f"Web research produced no usable results. {details}")

    coverage_note = ""
    if search_failures:
        coverage_note = "\n\nResearch coverage gaps:\n- " + "\n- ".join(search_failures) + "\n"

    synthesis_prompt = f"""You are an expert intelligence researcher.
Using all available search results below, write a complete, factual research brief
of approximately 600–800 words. Do not stop after the first findings.

Topic: {topic}

Requirements:
- Address each research question, and include relevant recent developments, actors,
  decisions, data points, outcomes, and emerging signals found in the results.
- Distinguish reported facts from interpretation; do not invent facts or dates.
- Note conflicting or weak evidence and identify material evidence gaps.
- Cite source URLs inline for key claims and finish with a concise source list.
- Avoid generic filler.

Search Findings:
{"".join(collected_info)}
{coverage_note}
"""

    available_output_tokens = GROQ_TPM_BUDGET - ceil(len(synthesis_prompt.encode("utf-8")) / 3) - 64
    if available_output_tokens < 900:
        raise ValueError(
            "Research findings exceed the safe Groq token budget for a complete "
            "synthesis. Reduce the topic scope or the amount of search context."
        )

    output_tokens = min(3000, available_output_tokens)
    response = invoke_model(llm, synthesis_prompt, max_output_tokens=output_tokens)
    if response.response_metadata.get("finish_reason") == "length":
        retry_output_tokens = min(4000, available_output_tokens)
        if retry_output_tokens <= output_tokens:
            raise RuntimeError(
                "Research synthesis was truncated at the safe Groq output limit. "
                "Narrow the topic or reduce the search context and try again."
            )
        response = invoke_model(llm, synthesis_prompt, max_output_tokens=retry_output_tokens)
        if response.response_metadata.get("finish_reason") == "length":
            raise RuntimeError(
                "Research synthesis remained truncated after retry. Narrow the topic and try again."
            )

    research_brief = response.content
    if isinstance(research_brief, list):
        research_brief = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in research_brief
        )
    if not isinstance(research_brief, str) or not research_brief.strip():
        raise RuntimeError("Research synthesis returned an empty response.")

    if search_failures:
        research_brief += "\n\n**Research coverage warning:** " + "; ".join(search_failures)
    return research_brief
