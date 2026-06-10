
import ollama
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Markdown, Static
from textual.containers import Vertical

from lore.context.builder import build_prompt
from lore.context.retriever import retrieve



class DashboardPane(Widget):

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Dashboard", id="dashboard_header"),
            Markdown("*Loading workspace summary...*", id="dashboard_content"),
        )
    
    def on_mount(self) -> None:
        self.run_worker(self.load_dashboard)

    async def load_dashboard(self) -> None:
        config = self.app.config
        if config.dashboard_cache_path.exists():
            cached = config.dashboard_cache_path.read_text(encoding="utf-8")
            self.query_one("#dashboard_content", Markdown).update(cached)
            return
        results = retrieve("What are the current milestones and what should I work on next?", config)
        prompt = build_prompt(results, "What are the current milestones and what should I work on next?")
        response = ollama.generate(
            model=config.model.watch,
            prompt=prompt,
            options={"temperature": 0, "num_predict": 1000},
        )
        self.query_one("#dashboard_content", Markdown).update(response['response'].strip())