# Lore
## The local-first developer workspace.
**Pre-Build Specification Document — v3.0**
June 2026

---

## 1. Project Overview

Lore is a fully local developer workspace. Drop in your spec, notes, and docs. The dashboard reads them and surfaces where you are — milestones, next steps, open questions. The agent takes a task description, retrieves the right context from everything in your workspace, plans, writes the code, and shows you the diff before a single file changes. Everything runs on your machine via Ollama. No API keys. No data leaves your device.

The positioning: your entire working context — docs, notes, decisions, code — in one place, fully local, with an AI that actually knows all of it.

### 1.1 The Problem

Knowledge is scattered. Your spec is in Notion. Your decisions are in a Google Doc. Your notes are in a scratchpad. Your code is in VS Code. When you sit down to build, you context-switch constantly — pulling up the spec to check a requirement, digging through notes to remember why you made a decision, alt-tabbing between four windows.

Lore solves this by being the primary window. Everything you need to think, plan, and build lives in one place, indexed locally, queryable by the agent at every step.

### 1.2 The Core Loop

1. Drop in your spec or docs
2. Dashboard reads them — shows milestone progress and suggested next steps
3. Open the agent, describe a task
4. Agent retrieves context from your entire workspace, generates a plan
5. You approve the plan, agent writes the code, shows the diff
6. Apply — files are written, workspace re-indexes

### 1.3 What Makes It Different

- **Fully local** — Ollama for LLM and embeddings. Zero cloud, zero API keys, zero data leaving the machine.
- **Workspace-first** — not a coding agent bolted onto a terminal. The workspace is the product. Docs, notes, agent, and dashboard are all first-class.
- **Context-grounded** — RAG retrieval before every agent step. The model sees your spec, your decisions, your notes — not generic context.
- **Knows your history** — git commits and ADRs are indexed. The agent knows why decisions were made, not just what the code looks like.
- **Keyboard-driven** — every pane is a toggle. No mouse required. Lives where you already think.
- **Context compounds** — every session, note, and agent task makes future tasks more accurate.

### 1.4 Portfolio Positioning

Lore demonstrates applied understanding of local LLM agent architecture, RAG pipelines, tool use via function calling, TUI application design, and product thinking. It is a complete, opinionated workspace — not a demo or a wrapper.

**Interview pitch:**
*"I built a fully local developer workspace — your docs, notes, and code in one place, with an AI that knows all of it. The key insight is that local LLMs fail not because of capability but because of context. I built a RAG engine that indexes your entire working context — specs, decisions, notes, git history — and retrieves exactly the right information before each agent step. That's what makes it work."*

---

## 2. Design Philosophy

Lore is built on one principle: **the developer is the architect, Lore is the builder.**

You decide what gets built. Lore figures out how, shows you the plan, does the work, and presents the result for your approval before a single file changes on disk. This is not an autonomous agent. It does not act in the background, make decisions on your behalf, or surprise you with changes.

Every agent task has exactly three developer checkpoints before any file is written:

1. **Context review** — see exactly what Lore loaded before it starts thinking
2. **Plan approval** — read the numbered plan, edit it, or cancel before any tool calls run
3. **Diff review** — see every changed line before [a]pply commits anything to disk

Outside these gates: ESC cancels at any stage. Deletes require a second explicit confirmation. Commands are displayed before they execute.

### 2.1 The Contractor Model

*"Think of Lore as a skilled contractor: you describe the job, they show you the blueprint, present the finished work for sign-off, and only start when you approve. They do not redesign your house while you sleep."*

---

## 3. Aesthetic

Lore is designed to be open all day. The visual language reflects that — calm, minimal, editorial. Not a hacker dashboard. Not a dev tool cobbled together. Something you'd want to look at for eight hours.

### 3.1 Color Palette — `earthy` theme

| Role | Hex | Usage |
|---|---|---|
| Background | `#1a1714` | App background — dark warm gray, brown undertone |
| Surface | `#252220` | Pane backgrounds, slightly lifted |
| Border | `#3a3530` | Pane borders — present but barely-there |
| Text primary | `#e8e0d5` | Main text — soft off-white, warm |
| Text muted | `#8a8078` | Secondary text, timestamps, labels |
| Accent | `#c4845a` | Muted terracotta — active states, highlights, progress |
| Accent alt | `#7a9e7e` | Sage green — success states, applied diffs |
| Warning | `#c9a84c` | Soft amber — warnings, pending confirmations |
| Error | `#b85c4a` | Muted red — errors only |

### 3.2 Typography and Layout

- Monospace font throughout — this is a terminal app
- Generous padding inside panes — content breathes
- Borders: single-line, warm gray, subtle
- Headers: uppercase, letter-spaced, muted — present but not loud
- No icons unless they add information. No decoration for its own sake.

---

## 4. Workspace Layout

Lore is a single canvas. The default state is the dashboard. Every other pane is a toggle — keyboard-driven, independent, and the layout reflows around whatever is visible.

### 4.1 Panes

| Pane | Keybind | Description |
|---|---|---|
| Dashboard | `Ctrl+H` | Home — milestone progress, to-dos, recent activity |
| Docs viewer | `Ctrl+D` | Read and scroll indexed documents |
| Notes | `Ctrl+N` | Quick capture — immediately indexed |
| Agent | `Ctrl+A` | Task → plan → diff → apply |
| Terminal | `Ctrl+T` | Toggleable shell for running commands |
| Chat | `Ctrl+Space` | Freeform Q&A against the full workspace |

### 4.2 Layout Behavior

- Panes stack horizontally by default — each toggle splits the available space
- Maximum two panes visible at once on narrow screens, three on wide
- Active pane has a slightly brighter border
- `ESC` always closes the frontmost pane or cancels the current action
- `Ctrl+Q` exits Lore entirely

### 4.3 Default State

Open Lore → Dashboard fills the screen. If no docs have been indexed yet, the dashboard shows an empty state with a prompt: *"Drop a spec or doc into your workspace to get started."*

---

## 5. Pane Specifications

### 5.1 Dashboard

The dashboard is generated by the LLM reading your indexed workspace. It is not a manually maintained kanban — it is inferred.

**Sections:**
- **Milestone progress** — reads your spec/docs, identifies milestones, estimates % complete based on agent session history and notes. Displayed as a simple progress bar per milestone.
- **Suggested next steps** — 3–5 action items inferred from what is in the spec vs. what has been done
- **Recent activity** — last agent session, last indexed file, last note captured
- **Open questions** — surfaces unresolved questions or decision points found in docs/notes

Dashboard content is regenerated on workspace open and after each agent session completes.

### 5.2 Docs Viewer

A scrollable document reader. Supports any file that has been indexed into the workspace — markdown, plain text, exported PDFs (as text).

- Syntax highlighted for markdown
- Section headers are navigable with `j`/`k` or arrow keys
- `Ctrl+F` to search within the document
- Active document shown in the pane header
- Multiple docs navigable via a mini file-list at the top of the pane

### 5.3 Notes / Brain Dump

A lightweight capture pane. Freeform text, no structure required. The moment you save (`Ctrl+S`), the note is chunked and indexed into ChromaDB with `source_type = "note"`.

- Each note is timestamped and stored in `.lore/notes/`
- Notes surface in dashboard (open questions, recent captures)
- Notes are available as context to the agent and chat
- `Ctrl+N` opens a new note. Previous notes browsable in a list above the editor.

### 5.4 Agent

Three-stage flow. Developer checkpoints at every stage.

**Stage 1 — Context Review**
- Task input: freeform text description
- Lore embeds the task, retrieves top-6 chunks from the full workspace (code, docs, notes, commits)
- Displays the loaded context: which files, which chunks, similarity scores
- Developer can proceed, discard a chunk, or cancel

**Stage 2 — Plan Approval**
- LLM generates a numbered plan from the task + context
- Developer reads, edits inline, or cancels
- `[p]roceed` runs the tool-calling loop. `ESC` cancels.

**Stage 3 — Diff Review**
- All file writes are queued — nothing touches disk until apply
- Unified diff shown with syntax highlighting
- `[a]pply` writes files, triggers re-index, saves session to SQLite
- `[i]terate` sends the diff back to the agent with additional instructions
- `[r]eject` discards all queued changes cleanly

### 5.5 Terminal

A real PTY shell — identical to your native terminal. Toggled in when you need to run commands (tests, builds, git). Toggled out when you don't.

- Supports vim, git, npm, any CLI tool
- No AI watch mode — the terminal is just a terminal
- Output is not monitored or intercepted

### 5.6 Chat

Freeform Q&A against the full workspace context. Ask about your spec, your notes, your code, your decisions. The LLM retrieves relevant chunks and answers with citations.

- `Ctrl+Space` opens/closes
- Conversation history persists within the session
- Citations shown inline: `[source: spec.md §4.2]`
- Uses the smaller/faster model (`qwen2.5-coder:7b` by default)

---

## 6. Tech Stack

A single Python package. Install Ollama, pull the models, run `pip install lore-dev`. No Docker, no servers, no configuration beyond a `config.toml`.

### 6.1 Dependencies

| Package | Role |
|---|---|
| `textual` | TUI framework — widgets, layout, reactivity |
| `typer` | CLI entry points |
| `chromadb` | Vector store for all indexed content |
| `sqlalchemy` | SQLite ORM — sessions, files, tool calls |
| `gitpython` | Git commit indexing |
| `watchdog` | File system watcher for re-indexing |
| `tiktoken` | Token counting for chunking |
| `tree-sitter` | AST chunking for TS/JS |
| `ollama` | LLM and embedding calls |
| `toml` | Config file parsing |

### 6.2 Models

| Model | Role |
|---|---|
| `qwen2.5-coder:14b` | Agent — planning, tool calling, diff generation |
| `qwen2.5-coder:7b` | Chat, dashboard inference, watch-mode (faster) |
| `nomic-embed-text` | Embeddings for all indexed content |

---

## 7. Context Engine

The context engine is what makes Lore useful. It indexes your entire workspace — code, docs, notes, git history — and retrieves precisely the relevant knowledge before each agent step or chat response.

### 7.1 What Gets Indexed

| Source | Collection | Boost |
|---|---|---|
| Source code | `{project}_code` | 1.00 |
| Git commits | `{project}_commits` | 1.10 |
| Docs / ADRs | `{project}_docs` | 1.05 (ADRs 1.15) |
| Notes | `{project}_notes` | 1.05 |

### 7.2 Retrieval Pipeline

1. Embed the input (task description, chat message, or note)
2. ChromaDB cosine search → top-k chunks across all collections
3. Apply source type boosts
4. Deduplicate: max 3 chunks per source file
5. Filter: cosine similarity ≥ `similarity_threshold` (default 0.70)
6. Return ordered results with metadata

### 7.3 Chunking Strategy

- **Python** — stdlib `ast` module. Functions and classes as atomic chunks.
- **TypeScript / JavaScript** — `tree-sitter`. Functions, arrow functions, classes.
- **Everything else** — sliding window (512 tokens, 50 token overlap).
- **Docs / notes / markdown** — sliding window with section boundary awareness.

### 7.4 Indexing Triggers

- `lore index` — manual full index
- File save — watchdog triggers re-index of changed file within 5 seconds
- Note capture — immediate index on `Ctrl+S`
- Agent apply — re-indexes all changed files after diff is applied
- Git poll — HEAD polled every 30 seconds, new commits indexed automatically

---

## 8. Agent Loop

### 8.1 Flow

```
task input
    → embed task → ChromaDB retrieval → apply boosts
    → display context to user
    → [proceed] → planning LLM call → display plan
    → [proceed] → tool-calling loop (max 30 calls)
        → all writes queued in diff.py, never to disk
    → generate unified diff
    → display diff to user
    → [apply] → write files → re-index → save session
    → [iterate] → feed diff back to agent with new instructions
    → [reject] → discard all queued changes
```

### 8.2 Tools

| Tool | Description |
|---|---|
| `read_file` | Read any file in the project |
| `write_file` | Queue a full file write (never immediate) |
| `create_file` | Queue a new file creation |
| `edit_file` | Queue a targeted edit (search/replace) |
| `delete_file` | Queue a deletion — flagged separately in diff, requires confirmation |
| `run_command` | Execute a shell command — displayed before running, 500ms pause |
| `list_directory` | List files and directories |
| `search_codebase` | Targeted mid-task ChromaDB retrieval |
| `read_url` | Fetch a URL and return its text content |

### 8.3 Safety Rules

- All file writes queue to `agent/diff.py` — nothing touches disk until `[a]pply`
- `delete_file` shown separately in diff view, requires explicit second confirmation
- `run_command` displays command text, pauses 500ms before executing
- `max_tool_calls = 30` enforced — raises `MaxToolCallsError` with a clear message
- All tool calls logged to `tool_calls` SQLite table

---

## 9. Storage Layer

### 9.1 Directory Structure

```
.lore/
  config.toml       project configuration
  lore.db           SQLite — files, commits, sessions, tool calls
  chroma/           ChromaDB persistent storage
  notes/            captured notes as markdown files
```

### 9.2 SQLite Schema

**files** — indexed file registry
**commits** — git commit index
**agent_sessions** — task, plan, status, file changes per session
**tool_calls** — every tool call logged with arguments and result

---

## 10. CLI

| Command | Description |
|---|---|
| `lore init` | Create `.lore/`, write default `config.toml`, check Ollama connectivity |
| `lore index` | Full index of current project |
| `lore` | Launch the workspace TUI |
| `lore agent "task"` | Open workspace directly into agent mode with a pre-filled task |
| `lore status` | Print indexed file count, commit count, last index timestamp |
| `lore note "text"` | Capture a note from the command line and index immediately |

---

## 11. config.toml

```toml
[project]
name = "my-project"

[model]
agent = "qwen2.5-coder:14b"
chat  = "qwen2.5-coder:7b"
embed = "nomic-embed-text"
ollama_url = "http://localhost:11434"

[indexing]
max_commits       = 50
git_poll_interval = 30
chunk_size        = 512
chunk_overlap     = 50
ignore            = ["node_modules/", "__pycache__/", "dist/", ".next/", "*.lock"]

[agent]
max_tool_calls        = 30
show_tool_calls       = true
run_command_pause_ms  = 500

[context]
similarity_threshold  = 0.70
top_k                 = 6
max_chunks_per_file   = 3
```

---

## 12. Phased Build Plan

Each phase ends with a working, demonstrable build.

### Phase 0 — Foundation ✅ (in progress)
- `pyproject.toml`, `src/lore/` package structure
- SQLite schema + SQLAlchemy models
- ChromaDB setup: collections, embed and query
- `config.py` with full defaults and TOML loader
- `ingestion/chunker.py` — AST + sliding window
- `ingestion/embedder.py` — Ollama nomic-embed-text

**Remaining:** `cli.py` — `lore init`, `lore index`, `lore status`

**Exit criteria:** `lore init` succeeds. `lore index` indexes a small project. A raw ChromaDB query returns relevant results.

---

### Phase 1 — Workspace Shell
- Textual app skeleton with the `earthy` theme applied globally
- Pane system: each pane is a widget, toggleable via keybinds
- Layout reflows correctly as panes open and close
- Header bar: project name, active model, index status dot
- Empty dashboard as default state — placeholder content
- `Ctrl+Q` exits. `ESC` closes frontmost pane.
- No AI yet. This phase is purely the shell and navigation.

**Exit criteria:** open Lore, toggle every pane in and out, layout reflows correctly, theme looks right.

---

### Phase 2 — Docs Viewer
- Drop a file into `.lore/docs/` — it gets indexed automatically
- Docs viewer pane: scrollable, markdown rendered, section navigation
- `Ctrl+F` search within document
- Multiple docs navigable from a file list at the top of the pane
- Watchdog triggers re-index on file changes inside `.lore/docs/`

**Exit criteria:** drop in the PRD, open docs viewer, read and navigate it inside Lore.

---

### Phase 3 — Dashboard
- LLM reads indexed docs and generates dashboard content
- Milestone progress: identifies milestones from spec, estimates % complete
- Suggested next steps: 3–5 action items inferred from spec vs. session history
- Recent activity: last agent session, last indexed file, last note
- Dashboard regenerates on workspace open and after each agent session
- Empty state prompt when no docs indexed

**Exit criteria:** drop in the PRD, open Lore, dashboard shows milestones and next steps inferred from the document.

---

### Phase 4 — Agent
- Agent pane: three-stage flow (context review → plan approval → diff review)
- Planning pass: LLM generates numbered plan before tool loop
- Tool calling loop: all 9 tools implemented
- Diff generation: unified diff from all queued writes
- `[a]pply`, `[i]terate`, `[r]eject` all working
- Apply triggers re-index of changed files
- Session saved to SQLite on completion
- Dashboard updates after apply

**Exit criteria:** describe a small feature. Lore generates a plan, implements it, shows a correct diff. Apply writes files. Dashboard reflects the completed work.

---

### Phase 5 — Notes
- Notes pane: freeform editor, `Ctrl+S` to save and index
- Notes stored in `.lore/notes/` as timestamped markdown files
- Notes surface in dashboard (recent captures, open questions)
- Notes available as context in agent and chat
- `lore note "text"` CLI command for quick capture

**Exit criteria:** capture a note, it appears in the dashboard, it surfaces as context in the next agent session.

---

### Phase 6 — Terminal
- PTY terminal pane, toggled with `Ctrl+T`
- Identical to native terminal — vim, git, npm all work
- No AI watch mode — terminal is just a terminal

**Exit criteria:** open terminal pane, run tests, close it. Shell state persists between toggles.

---

### Phase 7 — Chat
- Chat pane: freeform Q&A against full workspace context
- Retrieves chunks, answers with inline citations
- Conversation history persists within session
- Uses faster model (`qwen2.5-coder:7b`)

**Exit criteria:** ask a question about the spec. Chat returns an answer with a citation to the correct section.

---

### Phase 8 — Polish
- `lore history`: rich table of recent agent sessions
- Context transparency: show which chunks were loaded and their scores
- README: install guide, model pulls, `lore init` walkthrough
- Demo recording: full loop from spec drop to applied diff
- Future integrations groundwork: connector interface stubbed for Notion/Drive (local LLM sync, no cloud data)

**Exit criteria:** installable on a fresh machine via `pip install lore-dev`. Demo shows full loop in under 3 minutes.

---

## 13. Future: External Integrations

Not in scope for v1. Groundwork laid in Phase 8.

The principle: if Lore ever syncs from Notion, Google Drive, or SharePoint, the sync happens locally. Documents are pulled to `.lore/docs/`, indexed by the local RAG engine, and never sent to any external LLM. The integration is a data pipe — the intelligence stays on your machine.

Candidate integrations (future phases):
- Notion: export pages to `.lore/docs/` on a schedule
- Google Drive: watch a folder, pull `.md` and `.docx` files
- SharePoint: pull pages via MS Graph API

Each integration is opt-in, configured in `config.toml`, and runs as a background worker inside Textual.

---

## 14. Architecture Decision Records

**ADR-001: Ollama as Sole AI Backend**
Local-first is non-negotiable. Ollama provides a unified API for both LLM inference and embeddings. Adding cloud providers would undermine the core value proposition.

**ADR-002: Two Models — Agent vs. Chat/Dashboard**
The agent needs the strongest available model for planning and tool use. Chat and dashboard inference can use a smaller, faster model without quality loss. Separate config keys keep this explicit.

**ADR-003: Planning Step Before Tool Loop**
Giving the developer a plan to approve before any tool calls run is the primary safety mechanism. It also improves tool-call quality — the model reasons about the full task before acting.

**ADR-004: Diff Review Before Apply**
No file is written until the developer explicitly approves. This is the contract. Everything else in the safety model supports this guarantee.

**ADR-005: ChromaDB for Vectors, SQLite for Relational**
ChromaDB handles similarity search with project-scoped collections. SQLite handles structured records (sessions, tool calls, file registry). The two stores are complementary — never conflate them.

**ADR-006: Textual for TUI**
Textual provides a component model, reactive state, CSS-like theming, and async worker support. Building equivalent infrastructure on raw curses would cost weeks. Textual's constraints (no asyncio.create_task, post_message for cross-widget comms) are worth the tradeoff.

**ADR-007: Workspace-First, Terminal-Secondary**
The terminal is a pane, not the product. The workspace — docs, notes, dashboard, agent — is the product. This inversion from the original design reflects the core insight: the value is in the integrated context, not the shell wrapper.
