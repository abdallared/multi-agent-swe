import os
from langchain.tools import tool

@tool("Read file contents")
def read_file(file_path: str) -> str:
    """Useful to read the contents of a specific file in the project. The path should be relative to the project root."""
    print(f"\n[Tool] Reading file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"
