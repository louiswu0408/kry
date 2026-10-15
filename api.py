"""Rift Roast local FastAPI backend.

Run from this folder:
  python -m uvicorn api:app --reload
Then open http://127.0.0.1:8000/docs
"""

from collections import defaultdict
import os
from typing import Literal

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from ai_verdict import make_ai_verdict
from main import (
    account_by_riot_id,
    make_roast,
    match_detail,
    player_record,
    recent_match_ids,
    summarize,
)

load_dotenv(override=True)
app = FastAPI(title="Kry API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/report")
def report(
    riot_id: str,
    region: Literal["americas", "europe", "asia", "sea"] = "americas",
    count: int = Query(default=10, ge=1, le=100),
):
    """Retrieve one opt-in player's recent League statistics and playful banter."""
    api_key = os.getenv("RIOT_API_KEY", "").strip()
    if not api_key or api_key == "RGAPI_REPLACE_ME":
        raise HTTPException(status_code=500, detail="Set RIOT_API_KEY in your .env file.")

    try:
        with requests.Session() as session:
            session.headers.update({"X-Riot-Token": api_key})
            account = account_by_riot_id(session, riot_id, region)
            puuid = account["puuid"]
            match_ids = recent_match_ids(session, puuid, region, count)
            records = []
            for match_id in match_ids:
                record = player_record(match_detail(session, match_id, region), puuid)
                if record is not None:
                    records.append(record)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (RuntimeError, KeyError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not records:
        raise HTTPException(status_code=404, detail="No recent League matches found.")

    overall = summarize(records)
    grouped = defaultdict(list)
    for record in records:
        grouped[record["champion"]].append(record)
    champions = [
        {"champion": champion, **summarize(matches)}
        for champion, matches in sorted(
            grouped.items(), key=lambda item: len(item[1]), reverse=True
        )
    ]


    # Generate the original rule-based roast
    most_played = champions[0]
    if most_played["played"] >= 5:
        roast = (
            f"You've played {most_played['champion']} in {most_played['played']} "
            f"of your last {overall['played']} games. At this point, "
            "champion select is just a formality."
        )
    else:
        roast = make_roast(overall)

    if not roast:
        roast = "Some games are highlights. Others are character development."

    
    
    # Generate AI verdict
    verdict_source = "rule_based"

    print(
        "Gemini key loaded:",
        bool(os.getenv("GEMINI_API_KEY")),
        flush=True
    )

    if os.getenv("GEMINI_API_KEY"):
        try:
            print("Calling Gemini...", flush=True)

            ai_roast = make_ai_verdict(overall, champions)

            print("Gemini returned:", repr(ai_roast), flush=True)

            if ai_roast and ai_roast.strip():
                roast = ai_roast.strip()
                verdict_source = "gemini"
                print("AI verdict successful!", flush=True)

        except Exception as exc:
            print(
                f"AI ERROR: {type(exc).__name__}: {exc}",
                flush=True
            )



    return {
        "riot_id": f"{account.get('gameName', '')}#{account.get('tagLine', '')}",
        "region": region,
        "overall": overall,
        "champions": champions,
        "roast": roast,
        "verdict_source": verdict_source,
    }
