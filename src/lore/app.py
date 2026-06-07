
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static

class LoreApp(App):
    CSS_PATH = "lore.tcss"
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+h", "toggle_panel('dashboard')", "Dashboard"),
        Binding("ctrl+d", "toggle_panel('docs')", "Docs"),
        Binding("ctrl+n", "toggle_panel('notes')", "Notes"),
        Binding("ctrl+a", "toggle_panel('agent')", "Agent"),
        Binding("ctrl+t", "toggle_panel('terminal')", "Terminal"),
        Binding("ctrl+g", "toggle_panel('chat')", "Chat"),
        Binding("esc", "close_panel", "Close Panel"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Dashboard", id="dashboard")
        yield Static("Documentation", id="docs")
        yield Static("Notes", id="notes")
        yield Static("Agent", id="agent")
        yield Static("Terminal", id="terminal")
        yield Static("Chat", id="chat")

    def action_toggle_panel(self, panel_name: str) -> None:
        panel = self.query_one(f"#{panel_name}", Static)
        panel.display = not panel.display
