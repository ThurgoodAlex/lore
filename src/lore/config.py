"""
config.py — loads .lore/config.toml with fallback defaults.

Usage:
    cfg = load_config(project_root)
    cfg.model.agent        # "qwen2.5-coder:14b"
    cfg.watch.top_k        # 5
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import toml


@dataclass
class ModelConfig:
    agent: str = "qwen2.5-coder:14b"
    watch: str = "qwen2.5-coder:7b"
    embed: str = "nomic-embed-text"
    ollama_url: str = "http://localhost:11434"


@dataclass
class IndexingConfig:
    max_commits: int = 50
    git_poll_interval: int = 30
    chunk_size: int = 512
    chunk_overlap: int = 50
    ignore: List[str] = field(default_factory=lambda: [
        "node_modules/", "__pycache__/", "dist/", ".next/", "*.lock"
    ])


@dataclass
class AgentConfig:
    max_tool_calls: int = 30
    show_tool_calls: bool = True
    run_command_pause_ms: int = 500


@dataclass
class WatchConfig:
    similarity_threshold: float = 0.70
    top_k: int = 5
    terminal_buffer_lines: int = 30
    interjection_cooldown: int = 60


@dataclass
class ProjectConfig:
    name: str = "unnamed"


@dataclass
class Config:
    project: ProjectConfig = field(default_factory=ProjectConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    indexing: IndexingConfig = field(default_factory=IndexingConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    watch: WatchConfig = field(default_factory=WatchConfig)
    root: Path = field(default_factory=Path.cwd)

    @property
    def lore_dir(self) -> Path:
        return self.root / ".lore"

    @property
    def db_path(self) -> Path:
        return self.lore_dir / "lore.db"

    @property
    def chroma_dir(self) -> Path:
        return self.lore_dir / "chroma"

    @property
    def notes_dir(self) -> Path:
        return self.lore_dir / "notes"


def load_config(project_root: Path | str | None = None) -> Config:
    """Load config from .lore/config.toml, falling back to defaults."""
    root = Path(project_root) if project_root else _find_project_root()
    config_path = root / ".lore" / "config.toml"

    raw: dict = {}
    if config_path.exists():
        raw = toml.load(config_path)

    cfg = Config(root=root)

    if "project" in raw:
        p = raw["project"]
        cfg.project.name = p.get("name", cfg.project.name)

    if "model" in raw:
        m = raw["model"]
        cfg.model.agent = m.get("agent", cfg.model.agent)
        cfg.model.watch = m.get("watch", cfg.model.watch)
        cfg.model.embed = m.get("embed", cfg.model.embed)
        cfg.model.ollama_url = m.get("ollama_url", cfg.model.ollama_url)

    if "indexing" in raw:
        i = raw["indexing"]
        cfg.indexing.max_commits = i.get("max_commits", cfg.indexing.max_commits)
        cfg.indexing.git_poll_interval = i.get("git_poll_interval", cfg.indexing.git_poll_interval)
        cfg.indexing.chunk_size = i.get("chunk_size", cfg.indexing.chunk_size)
        cfg.indexing.chunk_overlap = i.get("chunk_overlap", cfg.indexing.chunk_overlap)
        cfg.indexing.ignore = i.get("ignore", cfg.indexing.ignore)

    if "agent" in raw:
        a = raw["agent"]
        cfg.agent.max_tool_calls = a.get("max_tool_calls", cfg.agent.max_tool_calls)
        cfg.agent.show_tool_calls = a.get("show_tool_calls", cfg.agent.show_tool_calls)
        cfg.agent.run_command_pause_ms = a.get("run_command_pause_ms", cfg.agent.run_command_pause_ms)

    if "watch" in raw:
        w = raw["watch"]
        cfg.watch.similarity_threshold = w.get("similarity_threshold", cfg.watch.similarity_threshold)
        cfg.watch.top_k = w.get("top_k", cfg.watch.top_k)
        cfg.watch.terminal_buffer_lines = w.get("terminal_buffer_lines", cfg.watch.terminal_buffer_lines)
        cfg.watch.interjection_cooldown = w.get("interjection_cooldown", cfg.watch.interjection_cooldown)

    return cfg


def _find_project_root() -> Path:
    """Walk up from cwd to find .lore/ directory, else return cwd."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".lore").is_dir():
            return parent
    return cwd


def write_default_config(project_root: Path) -> None:
    """Write a default config.toml into .lore/."""
    lore_dir = project_root / ".lore"
    lore_dir.mkdir(parents=True, exist_ok=True)
    config_path = lore_dir / "config.toml"
    if not config_path.exists():
        default = Config()
        data = {
            "project": {"name": project_root.name},
            "model": {
                "agent": default.model.agent,
                "watch": default.model.watch,
                "embed": default.model.embed,
                "ollama_url": default.model.ollama_url,
            },
            "indexing": {
                "max_commits": default.indexing.max_commits,
                "git_poll_interval": default.indexing.git_poll_interval,
                "chunk_size": default.indexing.chunk_size,
                "chunk_overlap": default.indexing.chunk_overlap,
                "ignore": default.indexing.ignore,
            },
            "agent": {
                "max_tool_calls": default.agent.max_tool_calls,
                "show_tool_calls": default.agent.show_tool_calls,
                "run_command_pause_ms": default.agent.run_command_pause_ms,
            },
            "watch": {
                "similarity_threshold": default.watch.similarity_threshold,
                "top_k": default.watch.top_k,
                "terminal_buffer_lines": default.watch.terminal_buffer_lines,
                "interjection_cooldown": default.watch.interjection_cooldown,
            },
        }
        with open(config_path, "w") as f:
            toml.dump(data, f)
