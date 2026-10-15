# Rift Roast — Python starter

A **consent-based** League of Legends statistics and playful-roast CLI. Start with your **own** Riot ID or a friend who wants to participate. Does not send chat messages, gather personal data, or target strangers.

## 1. Create your Riot API key

Sign in at https://developer.riotgames.com/. Copy your Development API Key; Riot development keys expire after 24 hours.

## 2. Install (Windows PowerShell)

In a PowerShell terminal from this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Replace `RGAPI_REPLACE_ME` in `.env` with your actual key. **Do not share your key or upload `.env` to GitHub.**

## 3. Try demo mode without a key

```powershell
.\.venv\Scripts\python.exe main.py --demo
```

## 4. Try your own account

```powershell
.\.venv\Scripts\python.exe main.py "Your Riot Name#NA1" --region americas --count 10
```

Put the Riot ID in quotes if it contains spaces. The hashtag is part of your actual Riot ID (it may *not* be `NA1`). The `--region` flag is an API routing cluster, **not** your Riot ID's tagline. Use `americas` for NA/BR/LAN/LAS, `europe` for EUW/EUNE/TR/RU, and `asia` for KR/JP. This first starter does not support SEA routing yet.

For quick iteration, use `--count 5`. Each match detail costs a request. No request is made in demo mode.

## 5. Run tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## How it works

1. Account-V1: `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` returns a **PUUID**.
2. Match-V5: `/lol/match/v5/matches/by-puuid/{puuid}/ids` returns match IDs.
3. Match-V5: `/lol/match/v5/matches/{matchId}` returns match data.
4. Find the participant with the exact PUUID and compute summary statistics.
5. Produce playful, statistics-only humor. No language-model/API key needed.

Win rate is wins / games. Overall KDA is (total kills + total assists) / total deaths; if no deaths occurred, we display *Perfect (0 deaths)*. The starter includes all recent game modes returned by the endpoint, so ranked-only averages require an additional queue filter in a later iteration.

## Common errors

- **401/403**: missing, invalid or expired API key. Refresh your development key.
- **404**: check `Name#Tagline`, whether the account exists, and the routing region.
- **429**: rate limit; retry later with a smaller `--count`.
- **No matches**: the account has no recent supported match records in that cluster.

## Next improvements

- Filtering queues (e.g., Ranked Solo/Duo vs ARAM)
- Cache retrieved games to avoid repeated API calls
- Tests with recorded, scrubbed API payloads
- FastAPI backend and React frontend
- Opt-in profiles and shareable dashboard, subject to Riot approval/policies for a public app

## Important

Development API access is for prototyping. A public product needs the appropriate Riot Developer Portal registration/approval. Don't use this project to harass other players or reveal hidden/personal information. Riot requires a notice that the app is not endorsed by Riot Games if publicly released.

Official documentation: https://developer.riotgames.com/docs/lol and https://developer.riotgames.com/docs/portal
