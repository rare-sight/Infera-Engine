from langchain_core.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """Search the web for recent and relevant information."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6))
        
        if not results:
            return "No results found."
        
        output = []
        for i, r in enumerate(results, 1):
            output.append(f"{i}. {r.get('title', '')}\n{r.get('body', '')}\nSource: {r.get('href', '')}\n")
        return "\n".join(output)
    except Exception as e:
        return f"Search error: {str(e)}"