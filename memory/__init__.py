"""
AI Software Company - Memory Module

Provides persistent long-term memory for learning from past projects.
Uses ChromaDB when available, falls back to JSON-based storage.
"""

from memory.vector_store import VectorStore, OllamaEmbedder
from memory.project_memory import ProjectMemory

__all__ = [
    'VectorStore',
    'OllamaEmbedder',
    'ProjectMemory',
]
