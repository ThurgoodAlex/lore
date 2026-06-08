import fnmatch

import typer
import ollama
import hashlib

from pathlib import Path

from lore.config import _find_project_root, load_config, write_default_config
from lore.storage.chroma import init_chroma
from lore.storage.db import Commit, init_db, upsert_file, Session, IndexedFile
from lore.ingestion.chunker import chunk_file
from lore.ingestion.embedder import embed_batch
from lore.storage.chroma import upsert_chunks
from lore.app import LoreApp


app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        LoreApp().run()


def _get_suffix(chunks: list) -> str:
    source_type = chunks[0].source_type
    suffix = {"code": "code", "doc": "docs", "adr": "docs", "note": "notes"}.get(source_type, "code")
    return suffix

def _check_ollama():
    try:
        ollama.list()
    except Exception as e:
        typer.echo("Ollama is not initialized. Please run 'ollama serve' and set up your models before using Lore.")
        raise typer.Exit(code=1) from e

def _initialize():
    _check_ollama()
    cfg = load_config()
    init_db(cfg.db_path)
    init_chroma(cfg.chroma_dir, cfg.project.name)
    return cfg


def _is_ignored(path: Path, ignore_patterns: list[str]) -> bool:
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path.name, pattern) or pattern.rstrip("/") in path.parts:
            return True
    return False

@app.command()
def init():
    cfg = _initialize()
    write_default_config(_find_project_root())
    typer.echo("Initialized Lore configuration in .lore/config.toml")
    typer.echo(f"Initialized Lore database at {cfg.db_path}")
    typer.echo(f"Initialized Chroma vector store at {cfg.chroma_dir} for project '{cfg.project.name}'")


@app.command()
def index():
    cfg = _initialize()
    typer.echo("Indexing project files and commit history...")
    for path in cfg.root.rglob("*"):
        if not _is_ignored(path, cfg.indexing.ignore) and path.is_file():
            typer.echo(f"Indexing {path}")
            source = path.read_text(encoding="utf-8", errors="ignore")
            content_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
            with Session() as s:
                existing = s.query(IndexedFile).filter_by(path=str(path)).first()
                if existing and existing.content_hash == content_hash:
                    typer.echo(f"Skipping {path} (unchanged)")
                    continue
            chunks = chunk_file(path, source, cfg)
            if not chunks:
                typer.echo(f"Warning: No chunks created for {path}")
                continue
            embeddings = embed_batch([chunk.text for chunk in chunks], cfg)
            documents = [c.text for c in chunks]
            metadatas = [
                {
                    "file_path": chunk.file_path,
                    "language": chunk.language,
                    "source_type": chunk.source_type,
                    "function_name": chunk.function_name or "",
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ]
            ids = [f"{path}:{chunk.chunk_index}" for chunk in chunks]
            upsert_chunks(_get_suffix(chunks), ids, embeddings, documents, metadatas)
            upsert_file(str(path), content_hash, chunks[0].source_type, chunks[0].language, len(chunks))
    typer.echo("Indexing complete.")

@app.command()
def status():
    with Session() as s:
        indexed_files = s.query(IndexedFile).count()
        commit_count = s.query(Commit).count()
        last_indexed = s.query(IndexedFile).order_by(IndexedFile.last_indexed.desc()).first()
    typer.echo(f"Indexed files: {indexed_files}")
    typer.echo(f"Indexed commits: {commit_count}")
    typer.echo(f"Last indexed: {last_indexed.last_indexed if last_indexed else 'N/A'}")

