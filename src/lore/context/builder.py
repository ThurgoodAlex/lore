import datetime
def build_prompt(results: list[dict], query: str) -> str:
    prompt = f"""You are analyzing a developer's local workspace.
Using only the context provided below, respond in markdown with exactly two sections:

## Milestones
List each build phase and whether it appears complete or in progress based on the context.
Today's date is {datetime.date.today()}. Distinguish between phases that are planned in documentation versus phases where code has actually been implemented. If only docs describe a phase, mark it as "Planned", not "Complete".

## Next Steps
List the 3 most important things to work on next based on the context.
For Next Steps, list specific, actionable tasks — not just phase names. Each step should be something that could be done in a single coding session.

If the context does not contain enough information to answer, say so explicitly. Do not invent information.\n\n"""
    for i, res in enumerate(results):
        prompt += f"Context {i+1} (source: {res['metadata']['source_type']}):\n{res['document']}\n\n"
    prompt += f"Question: {query}\nAnswer:"
    return prompt