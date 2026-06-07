# Lore — Claude Code Configuration

## What This Is
A fully local developer workspace with a terminal-native TUI (Textual).
One primary window: docs viewer, notes/brain dump, agent mode, terminal,
and a dashboard — all powered locally via Ollama. No cloud, no API keys.

GitHub: https://github.com/ThurgoodAlex/lore

## Product Direction (v3)
- **Workspace-first** — the dashboard is the default state, not a terminal
- **Toggleable panes** — each pane is keyboard-driven, independent, reflows on toggle
- **No terminal watch mode** — terminal is just a terminal, no AI interjections
- **Dashboard** — milestone progress and next steps inferred from indexed docs via LLM
- **Future integrations** — Notion/Drive sync planned but not in scope for v1

## Package Structure
src/lore/
  cli.py              Typer entry points: lore, lore init, lore index, lore status
  app.py              Textual Application class, keybindings, pane switching
  config.py           config.toml loader with defaults
  widgets/
    header.py         Header bar: project name, model, index status
    dashboard.py      Milestone progress, next steps, recent activity
    docs_viewer.py    Scrollable document reader
    notes.py          Freeform capture pane, immediate indexing on save
    agent_view.py     Agent mode: task input, context review, plan, diff review
    terminal.py       PTY Terminal widget wrapper (toggleable pane)
    chat.py           Freeform Q&A against full workspace context
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

## Phased Build Plan (v3)
- Phase 0: Foundation — storage, config, lore init, lore index, lore status ✅
- Phase 1: Workspace Shell — Textual app, earthy theme, toggleable pane system, keyboard nav
- Phase 2: Docs Viewer — drop a file, index it, read and scroll inside Lore
- Phase 3: Dashboard — milestone % and next steps inferred from indexed docs via LLM
- Phase 4: Agent — task → context review → plan → diff → apply
- Phase 5: Notes — freeform capture, immediate indexing, surfaces in dashboard + agent
- Phase 6: Terminal — toggleable PTY shell pane
- Phase 7: Chat — freeform Q&A against full workspace context
- Phase 8: Polish — lore history, README, demo, future integrations groundwork

## Earthy Theme (Textual CSS)
Background:    #1a1714   (dark warm gray, brown undertone)
Surface:       #252220   (pane backgrounds)
Border:        #3a3530   (subtle, barely-there)
Text primary:  #e8e0d5   (soft off-white, warm)
Text muted:    #8a8078   (labels, timestamps)
Accent:        #c4845a   (terracotta — active states, highlights, progress)
Accent alt:    #7a9e7e   (sage green — success, applied diffs)
Warning:       #c9a84c   (soft amber)
Error:         #b85c4a   (muted red)

## Pane Keybindings
Ctrl+H    Dashboard
Ctrl+D    Docs viewer
Ctrl+N    Notes
Ctrl+A    Agent
Ctrl+T    Terminal
Ctrl+Space  Chat
ESC       Close frontmost pane / cancel current action
Ctrl+Q    Quit

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
2. Display loaded context to user (transparency — they see what the agent knows)
3. agent/planner.py: LLM call → numbered plan string
4. User approves plan (widgets/agent_view.py)
5. agent/loop.py: tool-calling loop until model stops calling tools
   - All writes go to agent/diff.py queue (not to disk)
   - run_command tool shows command, pauses briefly before execution
6. agent/diff.py: generate unified diff from queued writes
7. User reviews diff — [a]pply, [i]terate, or [r]eject
8. On apply: diff.py writes files → ingestion/embedder.py re-indexes changed files

## Tool Safety Rules
- write_file, create_file, edit_file: ALWAYS queue, never write immediately
- delete_file: queue AND set requires_confirmation=True in the diff view
- run_command: display command text, pause 500ms before executing
- max_tool_calls enforced in agent/loop.py. Raise MaxToolCallsError if hit.
- All tool calls logged to tool_calls table via storage/db.py

## Context Retrieval Pattern
retriever.py query order:
1. Embed input (task description or note)
2. chroma.query(embedding, project_id, top_k=6)
3. apply_boosts(results): ADR x1.15, commit x1.10, doc x1.05, code x1.00
4. deduplicate: max 3 chunks per source file
5. filter: cosine similarity >= config.context.similarity_threshold

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
- Do not use asyncio.create_task() inside Textual widgets.
- Do not store embeddings in SQLite (ChromaDB only for vectors).
- Do not implement terminal watch mode — it was removed in v3.
- Do not make the terminal the default/primary pane — dashboard is the default.
