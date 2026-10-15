# trip-planner-agent

An AI trip planner built with Streamlit and an agentic tool-calling loop. Built for the Codecademy AI Engineer capstone (Trip Planner).

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
streamlit run app.py
pytest
```

Pick a destination, days, budget and interests in the sidebar, then click **Plan my trip**. Type feedback in the chat box and the agent revises the plan.

## What it demonstrates

| Requirement | Where |
|---|---|
| Streamlit app | `app.py` |
| Agent with tool calling | `agent.py`: the model chooses tools until it can answer |
| Real-time data integration | `tools.py`: live forecast from Open-Meteo, real places from OpenStreetMap |
| User feedback loop | chat box in `app.py`: feedback goes back to the agent, which revises the itinerary |

## How it works

1. Your trip details become a prompt
2. The model calls `get_weather` and `find_places`; each result is sent back to it
3. It writes a day-by-day itinerary that uses the forecast
4. Your feedback is appended to the same conversation and the loop runs again

## Layout

```
app.py       Streamlit UI and feedback chat
agent.py     tool-calling loop
tools.py     tool schemas and implementations
tests/       agent loop and tool tests (no network or API key needed)
```

## Limitations

- Place search is plain OpenStreetMap lookup, so it returns names and addresses but no ratings or opening hours
- No prices or bookings
- The conversation lives in the browser session only

MIT
