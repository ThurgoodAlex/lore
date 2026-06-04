"""
storage/db.py — SQLAlchemy models and session management.

Tables: files, commits, agent_sessions, tool_calls

Usage:
    from lore.storage.db import init_db, Session
    init_db(config)
    with Session() as s:
        s.add(...)
        s.commit()
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey,
    Integer, Text, create_engine, event
)
from sqlalchemy.orm import DeclarativeBase, Session as _Session, sessionmaker

_engine = None
_SessionLocal = None


class Base(DeclarativeBase):
    pass


class IndexedFile(Base):
    __tablename__ = "files"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    path         = Column(Text, nullable=False, unique=True)
    content_hash = Column(Text, nullable=False)
    source_type  = Column(Text, nullable=False, default="code")  # code|doc|adr|config|note
    language     = Column(Text, nullable=True)
    chunk_count  = Column(Integer, nullable=False, default=0)
    last_indexed = Column(DateTime, nullable=False, default=datetime.utcnow)


class Commit(Base):
    __tablename__ = "commits"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    hash          = Column(Text, nullable=False, unique=True)
    message       = Column(Text, nullable=False)
    author        = Column(Text, nullable=True)
    timestamp     = Column(DateTime, nullable=True)
    files_changed = Column(Text, nullable=True)   # JSON array
    indexed_at    = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    task            = Column(Text, nullable=False)
    plan            = Column(Text, nullable=True)   # JSON array of plan steps
    files_changed   = Column(Text, nullable=True)   # JSON array of {path, action}
    status          = Column(Text, nullable=False, default="in_progress")  # completed|rejected|iterated
    tool_call_count = Column(Integer, nullable=False, default=0)
    started_at      = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at    = Column(DateTime, nullable=True)


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("agent_sessions.id"), nullable=True)
    tool_name  = Column(Text, nullable=False)
    arguments  = Column(Text, nullable=True)   # JSON
    result     = Column(Text, nullable=True)   # truncated to 500 chars
    called_at  = Column(DateTime, nullable=False, default=datetime.utcnow)


def init_db(db_path: Path) -> None:
    """Create engine and all tables. Call once at startup."""
    global _engine, _SessionLocal

    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"
    _engine = create_engine(url, connect_args={"check_same_thread": False})

    # Enable WAL mode for better concurrency
    @event.listens_for(_engine, "connect")
    def set_wal(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA journal_mode=WAL")

    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)


@contextmanager
def Session() -> Generator[_Session, None, None]:
    """Context manager that yields a SQLAlchemy session."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --- Helpers ---

def log_tool_call(
    session_id: int | None,
    tool_name: str,
    arguments: dict,
    result: str,
) -> None:
    with Session() as s:
        s.add(ToolCall(
            session_id=session_id,
            tool_name=tool_name,
            arguments=json.dumps(arguments),
            result=result[:500],
        ))


def upsert_file(
    path: str,
    content_hash: str,
    source_type: str,
    language: str | None,
    chunk_count: int,
) -> None:
    with Session() as s:
        existing = s.query(IndexedFile).filter_by(path=path).first()
        if existing:
            existing.content_hash = content_hash
            existing.source_type  = source_type
            existing.language     = language
            existing.chunk_count  = chunk_count
            existing.last_indexed = datetime.utcnow()
        else:
            s.add(IndexedFile(
                path=path,
                content_hash=content_hash,
                source_type=source_type,
                language=language,
                chunk_count=chunk_count,
            ))
