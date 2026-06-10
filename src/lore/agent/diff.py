import difflib

from pathlib import Path

class DiffQueue:
    def __init__(self):
        self.queue = []
    
    def add_diff(self, path, content, operation):
        diff = {
            "path": path,
            "content": content,
            "operation": operation,  # "create", "edit", or "delete"
        }
        self.queue.append(diff)
    
    def generate_diffs(self):
        result = ""
        for file in self.queue:
            if Path(file["path"]).is_file():
                old_content = Path(file["path"]).read_text(encoding="utf-8", errors="ignore")
            else:
                old_content = ""
            new_content = file["content"]
            result += "".join(difflib.unified_diff(old_content.splitlines(keepends=True), new_content.splitlines(keepends=True), fromfile=file["path"], tofile=file["path"]))
        return result
    

    def apply(self):
        for file in self.queue:
            if file["operation"] in {"create", "edit"}:
                if not Path(file["path"]).parent.exists():
                    Path(file["path"]).parent.mkdir(parents=True, exist_ok=True)
                Path(file["path"]).write_text(file["content"], encoding="utf-8")
            elif file["operation"] == "delete":
                if Path(file["path"]).is_file():
                    Path(file["path"]).unlink()
        self.clear()

    def clear(self):
        self.queue = []