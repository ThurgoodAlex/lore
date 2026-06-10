
from pathlib import Path

from lore.agent.diff import DiffQueue
from lore.config import Config
import subprocess
import time

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path: str, content: str, diff_queue: DiffQueue):
    diff_queue.add_diff(path, content, "edit")

def create_file(path: str, content:str, diff_queue:DiffQueue):
    diff_queue.add_diff(path, content, "create")

def edit_file(path: str, old_str: str, new_str: str, diff_queue: DiffQueue):
    current = read_file(path)
    new_content = current.replace(old_str, new_str)
    diff_queue.add_diff(path, new_content, "edit")

def delete_file(path: str, diff_queue:DiffQueue):
    diff_queue.add_diff(path, None, "delete")

def list_files(directory: str) -> list[str]:
    p = Path(directory)
    return [str(f) for f in p.rglob("*") if f.is_file()]

def search_code(query: str, directory: str) -> list[str]:
    results = []
    for file in Path(directory).rglob("*"):
        if file.is_file():
            content = read_file(file)
            for i, line in enumerate(content.splitlines(), 1):   
                if query in line:
                    results.append(f"{file}:{i}:{line}")
    return results

def run_command(command: str, config: Config) -> str:
    time.sleep(config.agent.run_command_pause_ms / 1000)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def ask_user(question: str) -> str:
    return question
