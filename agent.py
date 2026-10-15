"""Tool-calling loop: the model decides which tools to call until it can answer."""
import os

import anthropic

from tools import TOOLS, run_tool

MODEL = os.environ.get("MODEL", "claude-haiku-5-5")

SYSTEM = (
    "You are a trip planning assistant. Before recommending anything, call get_weather for the "
    "destination and find_places for real places to visit. Reply with a day-by-day itinerary "
    "that takes the forecast into account. When the user gives feedback, revise the plan."
)


def chat(messages: list, client=None, max_steps: int = 8) -> str:
    """Append the model's turns (and tool results) to `messages`; return its final text."""
    client = client or anthropic.Anthropic()
    for _ in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=2000, system=SYSTEM, tools=TOOLS, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = [
            {"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
            for b in resp.content
            if b.type == "tool_use"
        ]
        messages.append({"role": "user", "content": results})
    return "I stopped after too many tool calls. Try a simpler request."
