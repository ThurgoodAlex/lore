"""
ingestion/chunker.py — AST-based chunking for Python/TS/JS, sliding window for everything else.

chunk_file(path, source, config) -> list[Chunk]
"""

from __future__ import annotations

import ast
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import tiktoken

from lore.config import Config

AST_EXTENSIONS = {".py", ".ts", ".js", ".tsx", ".jsx"}

_enc = tiktoken.get_encoding("cl100k_base")


@dataclass
class Chunk:
    text: str
    file_path: str
    chunk_index: int
    language: str
    function_name: Optional[str] = None
    source_type: str = "code"


def chunk_file(path: Path, source: str, config: Config) -> list[Chunk]:
    """Dispatch to AST or sliding-window chunker based on file extension."""
    ext = path.suffix.lower()
    language = _detect_language(ext)
    source_type = _detect_source_type(path)

    if ext == ".py":
        chunks = _chunk_python(source, str(path), config)
    elif ext in {".ts", ".js", ".tsx", ".jsx"}:
        chunks = _chunk_treesitter(source, str(path), ext, config)
    else:
        chunks = _sliding_window(source, str(path), language, config)

    # Override source_type for docs/ADRs
    for c in chunks:
        c.source_type = source_type

    return chunks


# --- Python AST chunker ---

def _chunk_python(source: str, filepath: str, config: Config) -> list[Chunk]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _sliding_window(source, filepath, "python", config)

    lines = source.splitlines()
    chunks: list[Chunk] = []
    idx = 0

    # Track parent class for methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in ast.walk(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    child._parent_class = node.name  # type: ignore[attr-defined]

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body_lines = lines[node.lineno - 1 : node.end_lineno]
            body = "\n".join(body_lines)

            header = f"File: {filepath}\n"
            parent = getattr(node, "_parent_class", None)
            if parent:
                header += f"Class: {parent}\n"

            text = header + body
            fn_name = node.name if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else None

            chunks.append(Chunk(
                text=text,
                file_path=filepath,
                chunk_index=idx,
                language="python",
                function_name=fn_name,
            ))
            idx += 1

    if not chunks:
        return _sliding_window(source, filepath, "python", config)
    return chunks


# --- tree-sitter chunker for TS/JS ---

def _chunk_treesitter(source: str, filepath: str, ext: str, config: Config) -> list[Chunk]:
    """Attempt tree-sitter AST chunking; fall back to sliding window."""
    try:
        import tree_sitter_typescript as tst
        import tree_sitter_javascript as tsj
        from tree_sitter import Language, Parser

        if ext in {".ts", ".tsx"}:
            lang = Language(tst.language_typescript())
        else:
            lang = Language(tsj.language_javascript())

        parser = Parser(lang)
        tree = parser.parse(source.encode())
        root = tree.root_node

        target_types = {
            "function_declaration",
            "arrow_function",
            "method_definition",
            "class_declaration",
        }

        source_lines = source.splitlines()
        chunks: list[Chunk] = []
        idx = 0

        def visit(node):
            nonlocal idx
            if node.type in target_types:
                start = node.start_point[0]
                end   = node.end_point[0] + 1
                body  = "\n".join(source_lines[start:end])
                text  = f"File: {filepath}\n{body}"
                fn_name = None
                for child in node.children:
                    if child.type == "identifier":
                        fn_name = child.text.decode()
                        break
                chunks.append(Chunk(
                    text=text,
                    file_path=filepath,
                    chunk_index=idx,
                    language=_detect_language(ext),
                    function_name=fn_name,
                ))
                idx += 1
            for child in node.children:
                visit(child)

        visit(root)

        if not chunks:
            return _sliding_window(source, filepath, _detect_language(ext), config)
        return chunks

    except Exception:
        return _sliding_window(source, filepath, _detect_language(ext), config)


# --- Sliding window chunker ---

def _sliding_window(source: str, filepath: str, language: str, config: Config) -> list[Chunk]:
    size    = config.indexing.chunk_size
    overlap = config.indexing.chunk_overlap

    tokens  = _enc.encode(source)
    chunks  = []
    idx     = 0
    start   = 0

    while start < len(tokens):
        end   = min(start + size, len(tokens))
        chunk_tokens = tokens[start:end]
        text  = f"File: {filepath}\n" + _enc.decode(chunk_tokens)
        chunks.append(Chunk(
            text=text,
            file_path=filepath,
            chunk_index=idx,
            language=language,
        ))
        idx   += 1
        start += size - overlap

    return chunks


# --- Helpers ---

def _detect_language(ext: str) -> str:
    return {
        ".py":   "python",
        ".ts":   "typescript",
        ".tsx":  "typescript",
        ".js":   "javascript",
        ".jsx":  "javascript",
        ".go":   "go",
        ".rs":   "rust",
        ".rb":   "ruby",
        ".java": "java",
        ".md":   "markdown",
        ".toml": "toml",
        ".json": "json",
        ".yaml": "yaml",
        ".yml":  "yaml",
    }.get(ext, "text")


_ADR_PATTERNS = re.compile(
    r"(adr[-_]\d+|architecture.decision|decision.record)",
    re.IGNORECASE,
)

def _detect_source_type(path: Path) -> str:
    name  = path.name.lower()
    parts = [p.lower() for p in path.parts]

    if _ADR_PATTERNS.search(str(path)):
        return "adr"
    if "docs" in parts or "documentation" in parts:
        return "doc"
    if name in {"readme.md", "readme.rst", "readme.txt"}:
        return "doc"
    if path.suffix.lower() in {".toml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".env"}:
        return "config"
    if ".lore/notes" in str(path).replace("\\", "/"):
        return "note"
    return "code"
