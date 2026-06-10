


import ollama

from lore.config import Config

def plan(task: str, context: list[dict], config: Config) -> str:
    """Given a task and relevant context, return a list of actions to take."""
    prompt = """You are a planning assistant. 
Given this task and context,
write a numbered step-by-step plan.
Be specific and concrete. Each step should be a single action.
"""

    for i, res in enumerate(context):
        prompt += f"Context {i+1} (source: {res['metadata']['source_type']}):\n{res['document']}\n\n"
    prompt += f"Task: {task}\nAnswer:"

    response = ollama.generate(
        model=config.model.agent,
        prompt=prompt,
        options={"temperature": 0.2, "num_predict": 1000},
    )
    return response['response'].strip()