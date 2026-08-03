from langchain_core.messages import HumanMessage
from core.models import get_groq_llm
from core.tools.search import web_search


def run_research_agent(topic: str, questions: list[str]) -> str:
    """
    Research Agent (stable version)
    - Manually runs web search for each question
    - Then asks Groq to synthesize the findings
    """
    llm = get_groq_llm()
    collected_info = []

    for question in questions:
        # 1. Search manually (no tool-calling issues)
        search_query = f"{question} {topic}"
        try:
            search_result = web_search.invoke(search_query)
        except Exception as e:
            search_result = f"Search failed: {str(e)}"

        collected_info.append(
            f"### Research Question\n{question}\n\n### Search Results\n{search_result}\n"
        )

    # 2. Synthesize with Groq
    synthesis_prompt = f"""You are an expert intelligence researcher.
Using the search results below, write a clear, factual research brief (300–400 words).

Topic: {topic}

Requirements:
- Focus on recent developments, key events, data points, and emerging signals
- Be specific and concrete
- Avoid generic filler

Search Findings:
{''.join(collected_info)}
"""

    response = llm.invoke([HumanMessage(content=synthesis_prompt)])
    return response.content