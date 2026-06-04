"""
storage/chroma.py — ChromaDB client wrapper.

Four collections per project:
  {name}_code     source code chunks
  {name}_commits  git commit content
  {name}_docs     ADRs, README, docs
  {name}_notes    auto-extracted decisions

Rule: ALWAYS pass where={'project_id': project_id} in every query.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

_client: chromadb.ClientAPI | None = None
_project_id: str = "default"


def init_chroma(chroma_dir: Path, project_id: str) -> None:
    global _client, _project_id
    chroma_dir.mkdir(parents=True, exist_ok=True)
    _client = chromadb.PersistentClient(
        path=str(chroma_dir),
        settings=Settings(anonymized_telemetry=False),
    )
    _project_id = project_id


def _col(suffix: str) -> chromadb.Collection:
    if _client is None:
        raise RuntimeError("ChromaDB not initialized. Call init_chroma() first.")
    name = f"{_project_id}_{suffix}"
    return _client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(
    suffix: str,
    ids: list[str],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    """Add or update chunks in a collection. Injects project_id into every metadata."""
    col = _col(suffix)
    for m in metadatas:
        m["project_id"] = _project_id
    col.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def delete_by_file(suffix: str, file_path: str) -> None:
    """Remove all chunks for a given file path."""
    col = _col(suffix)
    col.delete(where={"$and": [
        {"project_id": {"$eq": _project_id}},
        {"file_path": {"$eq": file_path}},
    ]})


def query(
    suffix: str,
    embedding: list[float],
    top_k: int = 10,
    extra_where: dict | None = None,
) -> list[dict[str, Any]]:
    """
    Query a collection. Returns list of dicts with keys:
      id, document, metadata, distance
    Always scoped to current project_id.
    """
    col = _col(suffix)

    where: dict = {"project_id": {"$eq": _project_id}}
    if extra_where:
        where = {"$and": [where, extra_where]}

    results = col.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    out = []
    if not results["ids"] or not results["ids"][0]:
        return out

    for i, doc_id in enumerate(results["ids"][0]):
        out.append({
            "id":       doc_id,
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return out


def query_all(
    embedding: list[float],
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Query all four collections and return merged results."""
    merged = []
    for suffix in ("code", "commits", "docs", "notes"):
        try:
            merged.extend(query(suffix, embedding, top_k=top_k))
        except Exception:
            pass
    return merged


def collection_count(suffix: str) -> int:
    try:
        return _col(suffix).count()
    except Exception:
        return 0


def total_chunk_count() -> int:
    return sum(collection_count(s) for s in ("code", "commits", "docs", "notes"))
