from langchain_core.messages import HumanMessage, SystemMessage
from core.models import get_groq_llm
from core.tools.search import web_search


def run_research_agent(topic: str, questions: list[str]) -> str:
    """
    Research Agent with iterative search capability.
    It can call the search tool multiple times.
    """
    llm = get_groq_llm()
    tools = [web_search]
    llm_with_tools = llm.bind_tools(tools)

    collected_info = []

    for question in questions:
        # First attempt
        messages = [
            SystemMessage(content="You are an expert research agent. Use the web_search tool when you need current information."),
            HumanMessage(content=f"Research this question thoroughly: {question}\n\nMain topic context: {topic}")
        ]

        response = llm_with_tools.invoke(messages)

        # If tool calls are requested
        if response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "web_search":
                    query = tool_call["args"].get("query", question)
                    search_result = web_search.invoke(query)
                    collected_info.append(f"### {question}\n{search_result}\n")
        else:
            collected_info.append(f"### {question}\n{response.content}\n")

    # Final synthesis
    synthesis_prompt = f"""You are a research synthesizer.
Combine the following research findings into one coherent, high-signal research brief (300-400 words).
Focus on facts, recent developments, data, and emerging signals.

Topic: {topic}

Research Findings:
{''.join(collected_info)}
"""

    final = llm.invoke([HumanMessage(content=synthesis_prompt)])
    return final.content