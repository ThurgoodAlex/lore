from pathlib import Path

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import ListView, Markdown, ListItem, Static
from textual.containers import VerticalScroll, Horizontal

class DocsViewerPane(Widget):
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            VerticalScroll(ListView()),
            VerticalScroll(
                Markdown("## Documentation Viewer\n\nUse this panel to view documentation files.", id="content")
            )
        )

    def load_file(self, file_path: Path) -> None:
        if file_path.is_file() and file_path.suffix in {".md", ".markdown", ".txt"}:
            content = file_path.read_text()
            self.query_one("#content", Markdown).update(content)

    def on_mount(self) -> None:
        files = Path(".").rglob("*.md")
        for file in files:
            item = ListItem(Static(file.name))
            item.file_path = file
            self.query_one(ListView).append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected_item = event.item
        if hasattr(selected_item, "file_path"):
            self.load_file(selected_item.file_path)