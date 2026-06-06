import os
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

@tool("Search the internet")
def search_internet(query: str) -> str:
    """Useful to search the internet about a given topic and return relevant results."""
    print(f"\n[Tool] Searching the internet for: {query}")
    try:
        search = DuckDuckGoSearchRun()
        result = search.run(query)
        return result
    except Exception as e:
        return f"Error performing search: {e}"
