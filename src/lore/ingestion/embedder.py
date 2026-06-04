"""
ingestion/embedder.py — Ollama nomic-embed-text embedding calls.

All calls are synchronous (run inside Textual workers).
"""

from __future__ import annotations

import ollama

from lore.config import Config


def embed_text(text: str, config: Config) -> list[float]:
    """Embed a single string. Returns a list of floats."""
    response = ollama.embeddings(
        model=config.model.embed,
        prompt=text,
    )
    return response["embedding"]


def embed_batch(texts: list[str], config: Config) -> list[list[float]]:
    """Embed multiple strings. Returns a list of embedding vectors."""
    return [embed_text(t, config) for t in texts]
