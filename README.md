# roadtrip-agent

Agent that plans multi-day road trips under budget and time constraints, with a validator that checks every itinerary.

Started as the Codecademy AI Engineer capstone (trip planner, Streamlit, agentic AI). `v1` is that baseline. `v2` adds real tools, constraint validation, and an eval suite to measure the difference.

```bash
pip install -r requirements.txt
cp .env.example .env        # add your LLM key
python plan.py "Fes to Merzouga, 4 days, 2 people, max 6000 MAD"
python evals/run.py --version v2
streamlit run app.py
```

Output is a validated JSON itinerary:

```json
{"days": [{"stops": ["Fes", "Midelt"], "drive_hours": 4.5, "cost": 1200}], "total_cost": 5400}
```

## Results

18 test trips in `evals/trips.jsonl`. A trip passes if it meets budget, daily driving limit, and uses only stops the geocoder can find.

| Version | Pass rate | Avg cost / trip | Avg latency |
|---|---|---|---|
| v1 (capstone baseline) | - | - | - |
| v2 (validator + real tools) | - | - | - |

By model (v2):

| Model | Pass rate | Cost | Latency |
|---|---|---|---|
| - | - | - | - |

Fill these in from `evals/run.py`. Don't commit numbers you didn't measure.

## What changed from v1

- Real distances and weather via OSRM and Open-Meteo instead of model guesses
- `validator.py` rejects bad plans and feeds the error back (max 3 retries)
- Pydantic schemas for the itinerary
- JSON traces of every agent step in `traces/`
- Docker image and a CI workflow that runs the tests

## Layout

```
plan.py        agent loop
tools.py       geocode, route, weather
schemas.py     Pydantic models
validator.py   constraint checks
app.py         Streamlit UI
evals/         test trips and runner
tests/         unit tests
```

## Known failures

Replace with what you actually observe, for example:
- Invents stops when the geocoder returns nothing
- Underestimates cost on long trips

## Run with Docker

```bash
docker build -t roadtrip-agent .
docker run -p 8501:8501 --env-file .env roadtrip-agent
```

MIT
