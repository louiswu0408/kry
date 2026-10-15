import { useState } from 'react';
import './App.css';

const REGIONS = [
  { value: 'americas', label: 'Americas (NA / LAN / LAS / BR)' },
  { value: 'europe', label: 'Europe (EUW / EUNE / TR / RU)' },
  { value: 'asia', label: 'Asia (KR / JP)' },
  { value: 'sea', label: 'Southeast Asia / Oceania' },
];

function number(value, digits = 1) {
  return value == null ? 'Perfect' : Number(value).toFixed(digits);
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <div className="metric__value">{value}</div>
      <div className="metric__label">{label}</div>
    </div>
  );
}

export default function App() {
  const [riotId, setRiotId] = useState('Krysten#cmd');
  const [region, setRegion] = useState('americas');
  const [count, setCount] = useState(10);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function generateReport(event) {
    event.preventDefault();
    setError('');
    setReport(null);

    if (!riotId.includes('#')) {
      setError('Enter your full Riot ID, such as Krysten#cmd.');
      return;
    }

    setLoading(true);
    try {
      const query = new URLSearchParams({
        riot_id: riotId.trim(),
        region,
        count: String(count),
      });
      const response = await fetch(`/api/report?${query.toString()}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : `Server returned HTTP ${response.status}`
        );
      }
      setReport(data);
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Cannot reach the backend. Is FastAPI running on port 8000?'
          : err.message || 'Something went wrong.'
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <div className="eyebrow">LEAGUE OF LEGENDS MATCH INSIGHTS</div>
        <h1>Kry</h1>
        <p>Bring your own Riot ID. Get the numbers, the champion breakdown, and a little playful banter.</p>
      </header>

      <section className="panel search-panel" aria-label="Find your match report">
        <form onSubmit={generateReport} className="search-form">
          <label className="field">
            <span>Your Riot ID</span>
            <input
              value={riotId}
              onChange={(event) => setRiotId(event.target.value)}
              placeholder="PlayerName#TAG"
              required
              maxLength={100}
            />
          </label>
          <label className="field">
            <span>API region</span>
            <select value={region} onChange={(event) => setRegion(event.target.value)}>
              {REGIONS.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </label>
          <label className="field small-field">
            <span>Recent games</span>
            <select value={count} onChange={(event) => setCount(Number(event.target.value))}>
              {[5, 10, 20, 50, 100].map((n) => (
                <option value={n} key={n}>{n}</option>
              ))}
            </select>
          </label>
          <button disabled={loading} type="submit">
            {loading ? 'Analyzing…' : 'Analyze my games →'}
          </button>
        </form>
        {error && <p className="error" role="alert">{error}</p>}
      </section>

      {!report && !loading && !error && (
        <div className="empty-state">Your match breakdown will appear here.</div>
      )}
      {loading && <div className="empty-state" role="status">Fetching recent matches from Riot…</div>}

      {report && (
        <section className="results" aria-live="polite">
          <div className="section-heading">
            <div>
              <div className="eyebrow">SUMMONER REPORT</div>
              <h2>{report.riot_id}</h2>
            </div>
            <span className="count-chip">Last {report.overall.played} matches</span>
          </div>

          <div className="metrics">
            <Metric label="Win rate" value={`${number(report.overall.win_rate)}%`} />
            <Metric label="Overall KDA" value={number(report.overall.kda, 2)} />
            <Metric label="Avg kills" value={number(report.overall.avg_kills)} />
            <Metric label="Avg deaths" value={number(report.overall.avg_deaths)} />
            <Metric label="Avg assists" value={number(report.overall.avg_assists)} />
          </div>

          <div className="two-columns">
            <article className="panel">
              <div className="eyebrow">THE VERDICT</div>
              <h3>Your roast</h3>
              <blockquote>“{report.roast}”</blockquote>
              <p className="hint">Just for fun — a small match sample isn't a skill rating.</p>
            </article>
            <article className="panel">
              <div className="eyebrow">CHAMPION BREAKDOWN</div>
              <h3>Most played</h3>
              <div className="champion-list">
                {report.champions.map((ch) => (
                  <div className="champion" key={ch.champion}>
                    <div className="champion-heading">
                      <strong>{ch.champion}</strong>
                      <span>{ch.played} {ch.played === 1 ? 'game' : 'games'} · {number(ch.win_rate)}% WR · {number(ch.kda, 2)} KDA</span>
                    </div>
                    <div className="bar-track" aria-label={`${ch.champion} played in ${ch.played} games`}>
                      <div className="bar-fill" style={{ width: `${ch.played / report.overall.played * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>
      )}
      <footer>Unofficial fan project. Not endorsed by Riot Games. Enter your own account or one you have permission to analyze.</footer>
    </main>
  );
}
