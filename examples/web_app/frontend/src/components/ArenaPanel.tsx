import { useState, useEffect, useRef } from "react";
import * as api from "../api";

interface TeamStub {
  id: number;
  name: string;
  agents: { id: number; name: string; avatar_emoji: string }[];
}

interface GameEvent {
  type: string;
  quarter: number;
  text: string;
  home_score: number;
  away_score: number;
}

export default function ArenaPanel() {
  const [teams, setTeams] = useState<TeamStub[]>([]);
  const [homeId, setHomeId] = useState<number | null>(null);
  const [awayId, setAwayId] = useState<number | null>(null);
  const [, setMatchId] = useState<number | null>(null);
  const [events, setEvents] = useState<GameEvent[]>([]);
  const [status, setStatus] = useState<"idle" | "live" | "finished">("idle");
  const feedRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    api.fetchTeams().then(setTeams).catch(() => {});
  }, []);

  // auto-scroll feed
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [events]);

  const lastEvent = events[events.length - 1];

  const handleStart = async () => {
    if (homeId === null || awayId === null || homeId === awayId) return;
    try {
      const m = await api.createMatch(homeId, awayId);
      setMatchId(m.id);
      setEvents([]);
      setStatus("live");

      // connect WS first, then start
      const ws = api.createMatchStream(m.id);
      wsRef.current = ws;
      ws.onmessage = (e) => {
        const evt: GameEvent = JSON.parse(e.data);
        setEvents((prev) => [...prev, evt]);
        if (evt.type === "final") {
          setStatus("finished");
        }
      };
      ws.onerror = () => setStatus("finished");

      // small delay to ensure WS subscription is ready
      await new Promise((r) => setTimeout(r, 500));
      await api.startMatch(m.id);
    } catch {
      alert("Match failed to start. Please ensure the backend is running correctly.");
    }
  };

  const handleReset = () => {
    wsRef.current?.close();
    setMatchId(null);
    setEvents([]);
    setStatus("idle");
    setHomeId(null);
    setAwayId(null);
  };

  const homeName = teams.find((t) => t.id === homeId)?.name ?? "Home Team";
  const awayName = teams.find((t) => t.id === awayId)?.name ?? "Away Team";

  return (
    <div>
      {status === "idle" && (
        <div className="card mb-32">
          <h3 className="section-title">⚔️ Match Setup</h3>
          {teams.length < 2 ? (
            <p style={{ color: "var(--text-2)" }}>
              At least 2 teams are required to start. Please create teams first!
            </p>
          ) : (
            <>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                <div className="form-group">
                  <label>Home Team</label>
                  <select
                    className="input"
                    value={homeId ?? ""}
                    onChange={(e) => setHomeId(Number(e.target.value))}
                  >
                    <option value="">Select Team…</option>
                    {teams.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name} ({t.agents.length} Players)
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Away Team</label>
                  <select
                    className="input"
                    value={awayId ?? ""}
                    onChange={(e) => setAwayId(Number(e.target.value))}
                  >
                    <option value="">Select Team…</option>
                    {teams.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name} ({t.agents.length} Players)
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <button
                className="btn btn-green btn-block"
                disabled={!homeId || !awayId || homeId === awayId}
                onClick={handleStart}
                style={{ marginTop: 8 }}
              >
                🏀 Tip Off!
              </button>
            </>
          )}
        </div>
      )}

      {(status === "live" || status === "finished") && (
        <>
          {/* Scoreboard */}
          <div className="scoreboard">
            <span className={`score-status ${status}`}>
              {status === "live" ? "● LIVE" : "✓ FINISHED"}
            </span>
            <div className="score-display">
              <div>
                <div className="score-team">{homeName}</div>
                <div className="score-num">{lastEvent?.home_score ?? 0}</div>
              </div>
              <div className="score-vs">VS</div>
              <div>
                <div className="score-team">{awayName}</div>
                <div className="score-num">{lastEvent?.away_score ?? 0}</div>
              </div>
            </div>
          </div>

          {/* Feed */}
          <div className="card">
            <h3 className="section-title" style={{ marginBottom: 12 }}>
              📺 Live Feed
            </h3>
            <div className="feed" ref={feedRef}>
              {events.map((ev, i) => (
                <div key={i} className={`feed-item ${ev.type}`}>
                  <span className="feed-quarter">Q{ev.quarter}</span>
                  <span className="feed-text">{ev.text}</span>
                </div>
              ))}
              {events.length === 0 && (
                <p style={{ textAlign: "center", color: "var(--text-2)", padding: 32 }}>
                  Waiting for Tip-Off…
                </p>
              )}
            </div>
          </div>

          {status === "finished" && (
            <button className="btn btn-ghost btn-block mt-12" onClick={handleReset}>
              ← Start New Match
            </button>
          )}
        </>
      )}
    </div>
  );
}
