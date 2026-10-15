# Kry — AI-Powered League of Legends Analytics & Roast Generator

**Kry** is a full-stack web application that analyzes League of Legends match history and generates personalized, AI-powered gameplay roasts.

Built with **React, FastAPI, Python, Riot Games API, and Google Gemini**, Kry transforms gameplay statistics into detailed performance summaries and sarcastic, statistics-based verdicts.

The application is designed for voluntary participation and focuses on gameplay performance rather than personal information or harassment.

## Features

- **Riot Games Integration:** Retrieve match history using a player's Riot ID.
- **Performance Analytics:** Calculate win rate, KDA, average kills, deaths, and assists.
- **Champion Statistics:** Analyze performance across individual champions.
- **AI-Powered Verdicts:** Generate personalized gameplay roasts using Google Gemini.
- **Nuclear Roast Mode:** Deliver aggressive, sarcastic gaming humor based on actual match statistics.
- **Fallback Generator:** Use predefined verdicts when the AI service is unavailable.
- **Interactive Dashboard:** View statistics and verdicts through a React web interface.
- **Match Count Selection:** Analyze different numbers of recent matches, subject to Riot API limits.

## Tech Stack

| Component | Technologies |
|---|---|
| Frontend | React, JavaScript, CSS, Vite |
| Backend | Python, FastAPI, Uvicorn |
| Game Data | Riot Games API (Account-V1, Match-V5) |
| AI Integration | Google Gemini API |
| HTTP Client | Python Requests |
| Development | Git, GitHub, VS Code |

## Project Structure

```text
kry/
├── api.py                 # FastAPI backend
├── main.py                # Riot API and statistics logic
├── ai_verdict.py          # Gemini verdict generation
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore
├── tests/                 # Python unit tests
└── frontend/
    ├── src/
    │   ├── App.jsx        # Main React interface
    │   ├── App.css
    │   ├── index.css
    │   └── main.jsx
    ├── package.json
    ├── vite.config.js
    └── index.html
```

## Getting Started

### 1. Prerequisites

Install the following:

- Python 3.10 or later
- Node.js and npm
- Git
- A Riot Games Development API key
- A Google Gemini API key (optional for AI verdicts)

### 2. Clone the Repository

```powershell
git clone https://github.com/louiswu0408/kry.git
cd kry
```

### 3. Configure the Backend

Create a Python virtual environment:

```powershell
py -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create the environment configuration:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```env
RIOT_API_KEY=your_riot_api_key
GEMINI_API_KEY=your_gemini_api_key
```

**Never commit `.env` or expose your API keys publicly.**

Riot development API keys expire after 24 hours and must be refreshed periodically.

### 4. Start the FastAPI Backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

The backend runs at:

http://127.0.0.1:8000

Interactive API documentation is available at:

http://127.0.0.1:8000/docs

### 5. Start the React Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the website at:

http://localhost:5173

Keep both the frontend and backend servers running during local development.

## How It Works

1. **Player Lookup:** The user enters a Riot ID and selects a routing region.
2. **Account Identification:** Riot Account-V1 resolves the Riot ID to a unique PUUID.
3. **Match Retrieval:** Match-V5 retrieves recent match IDs and detailed match information.
4. **Statistical Analysis:** Python calculates overall and champion-specific performance metrics.
5. **AI Verdict Generation:** Aggregated statistics are sent to Google Gemini to generate an original gameplay roast.
6. **Frontend Display:** React presents player statistics, champion performance, and the generated verdict.

If AI generation fails, Kry can fall back to its rule-based roast generator.

## Performance Metrics

Kry calculates the following metrics:

| Metric | Calculation |
|---|---|
| Win Rate | Wins / Matches × 100 |
| Average Kills | Total Kills / Matches |
| Average Deaths | Total Deaths / Matches |
| Average Assists | Total Assists / Matches |
| Overall KDA | (Total Kills + Total Assists) / Total Deaths |
| Champion Win Rate | Champion Wins / Champion Matches × 100 |

When total deaths equal zero, KDA is handled separately to avoid division by zero.

Small sample sizes may not accurately represent a player's long-term performance.

## API Endpoints

### GET /health

Checks whether the backend is running.

Example response:

```json
{
  "status": "ok"
}
```

### GET /report

Retrieves player