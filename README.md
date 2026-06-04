# Lore

A fully local developer workspace. Drop in your spec, notes, and docs. The dashboard reads them and surfaces where you are — milestones, next steps, open questions. The agent takes a task description, retrieves the right context from everything in your workspace, plans, writes the code, and shows you the diff before a single file changes.

Everything runs on your machine via Ollama. No API keys. No data leaves your device.

---

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com) running locally
- [Poetry](https://python-poetry.org)

## Models

Pull the required models before running Lore:

```bash
ollama pull qwen2.5-coder:14b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

## Installation

```bash
git clone https://github.com/ThurgoodAlex/lore.git
cd lore
poetry install
```

## Getting Started

Run these commands inside your project directory:

```bash
# Initialize Lore in your project
lore init

# Index your project files
lore index

# Check indexing status
lore status

# Launch the workspace
lore
```

## Stack

- **Textual** — terminal-native UI
- **ChromaDB** — local vector store for semantic search
- **SQLAlchemy** — SQLite for session and file tracking
- **Ollama** — local LLM inference and embeddings
- **qwen2.5-coder** — agent and chat model
- **nomic-embed-text** — embedding model
