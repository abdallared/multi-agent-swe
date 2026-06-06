import os
from crewai.tools import tool
from duckduckgo_search import DDGS

@tool("Search the internet")
def search_internet(query: str) -> str:
    """Useful to search the internet about a given topic and return relevant results."""
    print(f"\n[Tool] Searching the internet for: {query}")
    try:
        results = DDGS().text(query, max_results=3)
        return str(list(results))
    except Exception as e:
        return f"Error performing search: {e}"
