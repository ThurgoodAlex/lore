# Lore — Claude Code Configuration

## What This Is
A fully local AI coding agent with a terminal-native TUI (Textual).
Two modes: terminal mode (watch shell, interject on errors) and agent
mode (describe a task, Lore plans + writes code via tool calling).
Everything runs locally via Ollama. No cloud, no API keys.

## Package Structure
src/lore/
  cli.py              Typer entry points: lore, lore init, lore agent, etc.
  app.py              Textual Application class, keybindings, mode switching
  config.py           config.toml loader with defaults
  widgets/
    header.py         Header bar: project name, model, index status
    terminal.py       PTY Terminal widget wrapper
    ai_pane.py        Sliding bottom pane for watch-mode interjections
    agent_view.py     Full agent mode: task input, plan, diff review
    chat_overlay.py   Freeform chat overlay (Ctrl+Space)
  agent/
    loop.py           Tool-calling agent loop
    planner.py        Planning pass (generates plan before tool loop)
    tools.py          All 9 tool implementations
    diff.py           Queued write management and diff generation
  context/
    retriever.py      ChromaDB query, source boosts, deduplication
    builder.py        System prompt assembly
  ingestion/
    watcher.py        Watchdog file system observer
    git_indexer.py    GitPython commit indexer and HEAD poller
    chunker.py        AST + sliding window chunking
    embedder.py       Ollama nomic-embed-text embedding calls
  storage/
    db.py             SQLAlchemy models and session management
    chroma.py         ChromaDB client wrapper

## Dev Commands
poetry install
ollama pull qwen2.5-coder:14b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
poetry run lore init    # run inside a test project directory
poetry run lore index
poetry run lore
pytest tests/

## Phased Build Plan
- Phase 0: Foundation — storage, config, lore init, lore index (naive)
- Phase 1: Shell in a Box — Textual app + PTY terminal, no AI yet
- Phase 2: Context Engine — file watcher, git indexer, AST chunker
- Phase 3: Terminal Mode AI — error detection, AI pane, watch interjections
- Phase 4: Agent Mode — planning, tool loop, diff review, apply
- Phase 5: Polish — lore note, lore history, auto-doc extraction

## Conventions
- Textual: all state via reactive attributes. No globals.
- Textual: use self.run_worker() for all async ops (embedding, LLM calls).
  Never asyncio.create_task() inside a Textual app.
- Textual: cross-widget communication via post_message(). Never direct refs.
- SQLAlchemy: context managers everywhere. with Session() as s:
- ChromaDB: always pass where={'project_id': project_id} in every query.
  Never return results across project boundaries.
- Chunker: AST for .py .ts .js .tsx .jsx. Sliding window for everything else.
- Config: read from self.config. Never hardcode thresholds or model names.

## Agent Loop Pattern
1. context/retriever.py: embed task → ChromaDB search → apply boosts
2. agent/planner.py: LLM call → numbered plan string
3. User approves plan (widgets/agent_view.py)
4. agent/loop.py: tool-calling loop until model stops calling tools
   - All writes go to agent/diff.py queue (not to disk)
   - run_command tool shows command, pauses briefly before execution
5. agent/diff.py: generate unified diff from queued writes
6. User reviews diff (widgets/agent_view.py)
7. On apply: diff.py writes files → ingestion/embedder.py re-indexes changed files

## Tool Safety Rules
- write_file, create_file, edit_file: ALWAYS queue, never write immediately
- delete_file: queue AND set requires_confirmation=True in the diff view
- run_command: display command text, pause 500ms before executing
- max_tool_calls enforced in agent/loop.py. Raise MaxToolCallsError if hit.
- All tool calls logged to tool_calls table via storage/db.py

## Context Retrieval Pattern
retriever.py query order:
1. Embed input (task description or terminal snapshot)
2. chroma.query(embedding, project_id, top_k)
3. apply_boosts(results): ADR x1.15, commit x1.10, doc x1.05, code x1.00
4. deduplicate: max 3 chunks per source file
5. filter: cosine similarity >= config.watch.similarity_threshold

## Teaching Notes (how we work together)
- Explain the concept and the decision before writing the code
- After each section: zoom in and dissect — explain tradeoffs honestly
- Flag when something could have been done differently and why we chose this way
- User is a new grad learning architecture, RAG, agent loops, and Textual TUIs

## Do Not
- Do not add cloud AI providers. Ollama only.
- Do not write files from tool calls before user applies the diff.
- Do not skip the planning step in the agent loop.
- Do not call ChromaDB from the Textual main thread (use workers).
- Do not hardcode model names, thresholds, or chunk sizes.
- Do not stack AI panes in terminal mode (check pane visibility first).
- Do not use asyncio.create_task() inside Textual widgets.
- Do not store embeddings in SQLite (ChromaDB only for vectors).
