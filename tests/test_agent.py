from types import SimpleNamespace as NS

import agent
import tools


def test_agent_calls_a_tool_then_answers(monkeypatch):
    monkeypatch.setattr(agent, "run_tool", lambda name, args: '{"ok": true}')
    replies = iter([
        NS(stop_reason="tool_use", content=[NS(type="tool_use", id="t1", name="get_weather", input={"city": "Rabat"})]),
        NS(stop_reason="end_turn", content=[NS(type="text", text="Day 1: ...")]),
    ])
    client = NS(messages=NS(create=lambda **kw: next(replies)))

    messages = [{"role": "user", "content": "plan a trip"}]
    assert agent.chat(messages, client=client) == "Day 1: ..."
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    assert messages[2]["content"][0]["tool_use_id"] == "t1"


def test_agent_stops_after_max_steps():
    loop = NS(stop_reason="tool_use", content=[NS(type="tool_use", id="t", name="nope", input={})])
    client = NS(messages=NS(create=lambda **kw: loop))
    assert "too many tool calls" in agent.chat([{"role": "user", "content": "x"}], client=client, max_steps=2)


def test_unknown_tool_returns_error_text():
    assert "error" in tools.run_tool("does_not_exist", {})


def test_get_weather_formats_forecast(monkeypatch):
    monkeypatch.setattr(tools, "geocode", lambda city: (1.0, 2.0))
    daily = {"time": ["2026-10-15"], "temperature_2m_max": [24], "temperature_2m_min": [15], "precipitation_sum": [0.0]}
    monkeypatch.setattr(tools.httpx, "get", lambda *a, **k: NS(json=lambda: {"daily": daily}))
    assert tools.get_weather("Rabat", 1) == [{"date": "2026-10-15", "max_c": 24, "min_c": 15, "rain_mm": 0.0}]
