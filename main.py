"""Rift Roast: a consent-based League of Legends stats + playful roast CLI.

Use --demo to run without a Riot API key.
"""

import argparse
import os
from urllib.parse import quote
from collections import Counter
import requests
from dotenv import load_dotenv

REGIONS = ("americas", "europe", "asia", "sea")


def fetch_json(session, url, *, params=None):
    """Fetch JSON, converting common Riot API failures to helpful messages."""
    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        messages = {
            401: "Unauthorized: check your RIOT_API_KEY.",
            403: "Forbidden: your Riot API key may be expired or invalid.",
            404: "Not found: check your Riot ID and routing region.",
            429: "Rate limited: wait and try again with fewer matches.",
        }
        raise RuntimeError(messages.get(status, f"Riot API error (HTTP {status}).")) from exc
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError(f"Couldn't fetch Riot API data: {exc}") from exc


def account_by_riot_id(session, riot_id, region):
    if riot_id.count("#") != 1:
        raise ValueError('Use your full Riot ID, for example "Player Name#NA1".')
    game_name, tag_line = riot_id.rsplit("#", 1)
    if not game_name.strip() or not tag_line.strip():
        raise ValueError("Both your Riot game name and tagline are required.")
    url = (
        f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
        f"{quote(game_name, safe='')}/{quote(tag_line, safe='')}"
    )
    return fetch_json(session, url)


def recent_match_ids(session, puuid, region, count):
    url = (
        f"https://{region}.api.riotgames.com"
        f"/lol/match/v5/matches/by-puuid/{quote(puuid, safe='')}/ids"
    )

    return fetch_json(
        session,
        url,
        params={
            "start": 0,
            "count": count,
            "queue": 420
        }
    )

def match_detail(session, match_id, region):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{quote(match_id, safe='')}"
    return fetch_json(session, url)


def player_record(match, puuid):
    """Extract this player's match performance from a Match-V5 payload."""
    for player in match.get("info", {}).get("participants", []):
        if player.get("puuid") == puuid:
            return {
                "champion": player.get("championName", "Unknown"),
                "win": bool(player.get("win", False)),
                "kills": int(player.get("kills", 0)),
                "deaths": int(player.get("deaths", 0)),
                "assists": int(player.get("assists", 0)),
            }
    return None


def summarize(records):
    if not records:
        raise ValueError("No matches found to analyze.")
    n = len(records)
    kills = sum(r["kills"] for r in records)
    deaths = sum(r["deaths"] for r in records)
    assists = sum(r["assists"] for r in records)
    wins = sum(r["win"] for r in records)
    return {
        "played": n,
        "win_rate": 100 * wins / n,
        "avg_kills": kills / n,
        "avg_deaths": deaths / n,
        "avg_assists": assists / n,
        "kda": None if deaths == 0 else (kills + assists) / deaths,
    }


def make_roast(stats, records=None):
    if records:
        champions = Counter(
            r["champion"] for r in records
        )
        champion, games = champions.most_common(1)[0]

        if games >= 5:
            return (
                f"You've played {champion} in {games} of "
                f"your last {stats['played']} games. "
                "At this point, champion select "
                "is just a formality."
            )

    # Keep your existing roast conditions below

def print_report(riot_id, records):
    stats = summarize(records)
    print(f"\n=== Rift Roast: {riot_id} ===")
    print(f"Matches: {stats['played']}")
    print(f"Win rate: {stats['win_rate']:.1f}%")
    print(f"Avg K / D / A: {stats['avg_kills']:.1f} / {stats['avg_deaths']:.1f} / {stats['avg_assists']:.1f}")
    print(f"Overall KDA: {stats['kda']:.2f}" if stats["kda"] is not None else "Overall KDA: Perfect (0 deaths)")
    print(f"\nRoast: {make_roast(stats, records)}\n")
    print("Recent champions:", ", ".join(r["champion"] for r in records))
    champion_records = {}

    for record in records:
        champion = record["champion"]

        if champion not in champion_records:
            champion_records[champion] = []

        champion_records[champion].append(record)

    print("\n=== Champion Statistics ===")

    for champion, games in sorted(
        champion_records.items(),
        key=lambda x: len(x[1]),
        reverse=True
    ):
        stats = summarize(games)

        print(f"\n{champion}:")
        print(f"  Games: {stats['played']}")
        print(f"  Win rate: {stats['win_rate']:.1f}%")
        print(f"  Avg kills: {stats['avg_kills']:.1f}")
        print(f"  Avg deaths: {stats['avg_deaths']:.1f}")
        print(f"  KDA: {stats['kda']:.2f}" if stats["kda"] is not None
            else "  KDA: Perfect (0 deaths)")

def demo_records():
    return [
        {"champion": "Yasuo", "win": False, "kills": 4, "deaths": 10, "assists": 6},
        {"champion": "Ahri", "win": False, "kills": 6, "deaths": 9, "assists": 7},
        {"champion": "Lux", "win": True, "kills": 3, "deaths": 7, "assists": 12},
        {"champion": "Yasuo", "win": False, "kills": 2, "deaths": 11, "assists": 3},
        {"champion": "Jinx", "win": False, "kills": 7, "deaths": 8, "assists": 4},
    ]


def main():
    parser = argparse.ArgumentParser(description="Summarize your League stats and get a playful roast.")
    parser.add_argument("riot_id", nargs="?", help='Your Riot ID in quotes, e.g. "Name#NA1"')
    parser.add_argument("--region", choices=REGIONS, default="americas", help="Routing cluster; NA = americas")
    parser.add_argument("--count", type=int, default=10, help="Recent games to analyze (1-20)")
    parser.add_argument("--demo", action="store_true", help="Try offline with mock statistics (no API key)")
    args = parser.parse_args()

    if args.demo:
        print("DEMO MODE: these stats are fictional, not real Riot data.")
        print_report("DemoPlayer#NA1", demo_records())
        return

    if not args.riot_id:
        parser.error('enter your Riot ID, e.g. "YourName#NA1", or run --demo')
    if not 1 <= args.count <= 20:
        parser.error("--count must be between 1 and 100")

    load_dotenv(override=True)
    api_key = os.getenv("RIOT_API_KEY", "").strip()
    if not api_key or api_key == "RGAPI_REPLACE_ME":
        parser.error("add RIOT_API_KEY to your .env file (see README.md).")

    with requests.Session() as session:
        session.headers.update({"X-Riot-Token": api_key})
        try:
            account = account_by_riot_id(session, args.riot_id, args.region)
            puuid = account["puuid"]
            match_ids = recent_match_ids(session, puuid, args.region, args.count)
            print("Account found:", account.get("gameName"), account.get("tagLine"))
            print("Region:", args.region)
            print("Match IDs:", match_ids)
            if not match_ids:
                print("No recent League matches found for that Riot ID in this region.")
                return

            records = []
            for match_id in match_ids:
                match = match_detail(session, match_id, args.region)
                record = player_record(match, puuid)
                if record is not None:
                    records.append(record)
            if not records:
                print("No matching participant records found in the returned matches.")
                return
            print_report(args.riot_id, records)
        except (RuntimeError, ValueError, KeyError) as exc:
            parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
