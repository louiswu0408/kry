"""Kry public website entry point.

Hosts the built React frontend and a demo-safe report endpoint under one domain.
DEMO_MODE=1 is the intended setting until Riot approves a production API key.
"""

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Kry", version="1.0.0")


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "demo" if os.getenv("DEMO_MODE", "1") == "1" else "live"}


def sample_report(region: str):
    """Clearly labeled synthetic example; NEVER derived from a visitor's Riot ID."""
    return {
        "riot_id": "DemoPlayer#NA1",
        "region": region,
        "demo_mode": True,
        "notice": "DEMO ONLY — fictional statistics, not a real Riot account lookup.",
        "overall": {
            "played": 10,
            "win_rate": 40.0,
            "avg_kills": 7.3,
            "avg_deaths": 5.3,
            "avg_assists": 5.8,
            "kda": 131 / 53,
        },
        "champions": [
            {
                "champion": "Fiora",
                "played": 7,
                "win_rate": 2 / 7 * 100,
                "avg_kills": 55 / 7,
                "avg_deaths": 39 / 7,
                "avg_assists": 45 / 7,
                "kda": 100 / 39,
            },
            {
                "champion": "Jax",
                "played": 2,
                "win_rate": 50.0,
                "avg_kills": 5.0,
                "avg_deaths": 5.0,
                "avg_assists": 2.5,
                "kda": 1.5,
            },
            {
                "champion": "Jinx",
                "played": 1,
                "win_rate": 100.0,
                "avg_kills": 8.0,
                "avg_deaths": 4.0,
                "avg_assists": 8.0,
                "kda": 4.0,
            },
        ],
        "roast": (
            "Seven Fiora games and only two wins? The Grand Duelist "
            "is apparently hosting an enemy-top-laner charity tournament. "
            "Your 2.56 KDA is doing its best, but the victory screen "
            "still has you on its block list."
        ),
        "verdict_source": "demo",
    }


@app.get("/api/report")
def report(
    riot_id: str,
    region: Literal["americas", "europe", "asia", "sea"] = "americas",
    count: int = Query(default=10, ge=1, le=100),
):
    if os.getenv("DEMO_MODE", "1") == "1":
        return sample_report(region)

    # Live public usage requires a Riot PRODUCTION key, opt-in flow,
    # request throttling, caching and compliance review beforehand.
    if os.getenv("RIOT_PRODUCTION_APPROVED") != "1":
        raise HTTPException(
            status_code=503,
            detail="Live Riot lookups are not enabled. Try the public demo.",
        )

    from api import report as live_report  # Imported only when live mode is approved
    return live_report(riot_id=riot_id, region=region, count=count)


static_dir = Path(__file__).resolve().parent / "frontend" / "dist"
if not static_dir.is_dir():
    raise RuntimeError(
        "Built frontend not found. Build with 'cd frontend && npm run build' "
        "or deploy using the included Dockerfile."
    )

# Keep this LAST so /api/report, /api/health and /docs take precedence.
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")
