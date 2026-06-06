"""
Vector Store — Persistent vector memory with ChromaDB or JSON fallback.

Provides a unified interface for storing and querying document embeddings.
Uses Ollama's /api/embed endpoint with the configured EMBEDDINGS_MODEL
for generating embeddings.

If chromadb is not installed, falls back to a lightweight JSON-based store
with manual cosine-similarity search (no numpy required).
"""

import hashlib
import json
import logging
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# ── Try to import ChromaDB ──────────────────────────────────────
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    HAS_CHROMADB = True
    logger.info("ChromaDB available — using vector database backend")
except ImportError:
    HAS_CHROMADB = False
    logger.info("ChromaDB not installed — using JSON fallback for memory")


# ═════════════════════════════════════════════════════════════════
# Embedding Helper
# ═════════════════════════════════════════════════════════════════

class OllamaEmbedder:
    """Generate embeddings via Ollama's /api/embed endpoint."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "bge-m3:latest"):
        self.base_url = base_url
        self.model = model

    def embed(self, text: str) -> List[float]:
        """Generate an embedding vector for a single text."""
        try:
            response = requests.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": text},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            # Ollama returns {"embeddings": [[...vector...]]}
            embeddings = data.get("embeddings") or data.get("embedding")
            if isinstance(embeddings, list) and len(embeddings) > 0:
                # /api/embed returns list of lists
                if isinstance(embeddings[0], list):
                    return embeddings[0]
                return embeddings

            raise ValueError(f"Unexpected embedding response format: {list(data.keys())}")

        except requests.exceptions.ConnectionError:
            logger.warning("Ollama not reachable for embeddings — returning empty vector")
            return []
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(t) for t in texts]


# ═════════════════════════════════════════════════════════════════
# JSON Fallback Store
# ═════════════════════════════════════════════════════════════════

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity without numpy — pure Python."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class _JSONStore:
    """
    Simple JSON-file-based vector store — fallback when ChromaDB is unavailable.

    Data format:
    {
        "documents": {
            "<id>": {
                "text": "...",
                "embedding": [...],
                "metadata": {...},
                "added_at": 1234567890.0
            }
        }
    }
    """

    def __init__(self, persist_path: str):
        self.path = Path(persist_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = {"documents": {}}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.debug(f"JSON store loaded: {len(self._data['documents'])} documents")
            except (json.JSONDecodeError, KeyError):
                logger.warning("Corrupt JSON store — starting fresh")
                self._data = {"documents": {}}

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False)

    def add(self, doc_id: str, text: str, embedding: List[float], metadata: Dict = None):
        self._data["documents"][doc_id] = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
            "added_at": time.time(),
        }
        self._save()

    def query(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Find top-k most similar documents by cosine similarity."""
        if not query_embedding:
            return []

        scored = []
        for doc_id, doc in self._data["documents"].items():
            emb = doc.get("embedding", [])
            sim = _cosine_similarity(query_embedding, emb)
            scored.append({
                "id": doc_id,
                "text": doc["text"],
                "metadata": doc.get("metadata", {}),
                "similarity": sim,
            })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def delete(self, doc_id: str) -> bool:
        if doc_id in self._data["documents"]:
            del self._data["documents"][doc_id]
            self._save()
            return True
        return False

    def count(self) -> int:
        return len(self._data["documents"])

    def clear(self):
        self._data = {"documents": {}}
        self._save()


# ═════════════════════════════════════════════════════════════════
# ChromaDB Store
# ═════════════════════════════════════════════════════════════════

class _ChromaStore:
    """ChromaDB-backed vector store with persistent storage."""

    def __init__(self, persist_dir: str, collection_name: str = "projects"):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, doc_id: str, text: str, embedding: List[float], metadata: Dict = None):
        if not embedding:
            logger.warning(f"Empty embedding for doc {doc_id} — skipping")
            return

        # ChromaDB metadata values must be str, int, float, or bool
        clean_meta = {}
        if metadata:
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)

        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[clean_meta] if clean_meta else None,
        )

    def query(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        if not query_embedding:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count() or 1),
            include=["documents", "metadatas", "distances"],
        )

        items = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns distances (lower = more similar for cosine)
                distance = results["distances"][0][i] if results["distances"] else 0
                items.append({
                    "id": doc_id,
                    "text": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "similarity": 1.0 - distance,  # Convert distance to similarity
                })

        return items

    def delete(self, doc_id: str) -> bool:
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def count(self) -> int:
        return self.collection.count()

    def clear(self):
        # Delete and recreate the collection
        name = self.collection.name
        meta = self.collection.metadata
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata=meta,
        )


# ═════════════════════════════════════════════════════════════════
# Public VectorStore (unified interface)
# ═════════════════════════════════════════════════════════════════

class VectorStore:
    """
    Persistent vector memory — uses ChromaDB if available, JSON fallback otherwise.

    Usage:
        store = VectorStore(persist_dir="./memory/db")
        store.add("proj_1", "task manager app with auth", embedding_vec, {"quality": 85})
        results = store.query("todo app with login", query_embedding)
    """

    def __init__(
        self,
        persist_dir: str = "./memory/db",
        collection_name: str = "projects",
        embedder: Optional[OllamaEmbedder] = None,
    ):
        self.persist_dir = persist_dir
        self.embedder = embedder

        if HAS_CHROMADB:
            os.makedirs(persist_dir, exist_ok=True)
            self._store = _ChromaStore(persist_dir, collection_name)
            self.backend = "chromadb"
            logger.info(f"VectorStore initialized with ChromaDB at {persist_dir}")
        else:
            json_path = os.path.join(persist_dir, f"{collection_name}.json")
            os.makedirs(persist_dir, exist_ok=True)
            self._store = _JSONStore(json_path)
            self.backend = "json"
            logger.info(f"VectorStore initialized with JSON fallback at {json_path}")

    def add(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict] = None,
        embedding: Optional[List[float]] = None,
    ):
        """
        Add or update a document in the store.

        If no embedding is provided and an embedder is configured, one is
        generated automatically from the text.
        """
        if embedding is None and self.embedder:
            embedding = self.embedder.embed(text)

        if not embedding:
            logger.warning(f"No embedding for doc '{doc_id}' — cannot store")
            return

        self._store.add(doc_id, text, embedding, metadata)
        logger.debug(f"Stored document '{doc_id}' ({len(embedding)}-dim)")

    def query(
        self,
        text: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        top_k: int = 3,
    ) -> List[Dict]:
        """
        Find the top-k most similar documents.

        Provide either `text` (auto-embedded) or a pre-computed `embedding`.
        """
        if embedding is None and text and self.embedder:
            embedding = self.embedder.embed(text)

        if not embedding:
            logger.warning("No embedding for query — returning empty results")
            return []

        return self._store.query(embedding, top_k)

    def delete(self, doc_id: str) -> bool:
        """Remove a document by ID."""
        return self._store.delete(doc_id)

    def count(self) -> int:
        """Number of stored documents."""
        return self._store.count()

    def clear(self):
        """Remove all documents."""
        self._store.clear()
        logger.info("VectorStore cleared")

    @staticmethod
    def make_id(text: str) -> str:
        """Generate a deterministic document ID from text."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
