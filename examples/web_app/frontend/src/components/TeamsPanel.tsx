import React, { useState, useEffect } from "react";
import * as api from "../api";

interface AgentStub {
  id: number;
  name: string;
  avatar_emoji: string;
}

interface TeamData {
  id: number;
  name: string;
  agents: AgentStub[];
}

export default function TeamsPanel() {
  const [teams, setTeams] = useState<TeamData[]>([]);
  const [agents, setAgents] = useState<AgentStub[]>([]);
  const [teamName, setTeamName] = useState("");
  const [selected, setSelected] = useState<number[]>([]);

  const load = async () => {
    try {
      const [t, a] = await Promise.all([api.fetchTeams(), api.fetchAgents()]);
      setTeams(t);
      setAgents(a);
    } catch {
      /* */
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggle = (id: number) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 5 ? [...prev, id] : prev
    );
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teamName || selected.length === 0) return;
    try {
      await api.createTeam(teamName, selected);
      setTeamName("");
      setSelected([]);
      await load();
    } catch {
      alert("Failed to create team");
    }
  };

  const handleDelete = async (id: number) => {
    await api.deleteTeam(id);
    await load();
  };

  return (
    <div>
      <div className="card mb-32">
        <h3 className="section-title">🏟️ Build Teams</h3>
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label>Team Name</label>
            <input
              className="input"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              placeholder="e.g. Neural Network Team"
            />
          </div>
          <div className="form-group">
            <label>Select Players (1–5)</label>
            {agents.length === 0 ? (
              <p style={{ color: "var(--text-2)", fontSize: "0.9rem" }}>
                No available agents. Please create agents first!
              </p>
            ) : (
              agents.map((a) => (
                <div
                  key={a.id}
                  className={`agent-select-item ${selected.includes(a.id) ? "selected" : ""}`}
                  onClick={() => toggle(a.id)}
                >
                  <span style={{ fontSize: "1.5rem" }}>{a.avatar_emoji}</span>
                  <span style={{ fontWeight: 600, color: "var(--text-0)" }}>{a.name}</span>
                  {selected.includes(a.id) && (
                    <span style={{ marginLeft: "auto", color: "var(--blue)" }}>✓</span>
                  )}
                </div>
              ))
            )}
          </div>
          <button
            type="submit"
            className="btn btn-orange btn-block"
            disabled={!teamName || selected.length === 0}
          >
            🛡️ Create Team ({selected.length}/5)
          </button>
        </form>
      </div>

      {teams.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🛡️</div>
          <p>No teams yet. Create your first team above!</p>
        </div>
      ) : (
        <div className="card-grid">
          {teams.map((t) => (
            <div key={t.id} className="card agent-card">
              <button className="agent-delete" onClick={() => handleDelete(t.id)} title="Delete">
                ✕
              </button>
              <div className="agent-name">{t.name}</div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {t.agents.map((a) => (
                  <span
                    key={a.id}
                    style={{
                      background: "var(--bg-3)",
                      padding: "4px 10px",
                      borderRadius: 6,
                      fontSize: "0.85rem",
                    }}
                  >
                    {a.avatar_emoji} {a.name}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
