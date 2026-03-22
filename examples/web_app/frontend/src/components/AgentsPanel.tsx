import React, { useState, useEffect } from "react";
import * as api from "../api";
import AgentCard, { type AgentData } from "./AgentCard";

export default function AgentsPanel() {
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [name, setName] = useState("");
  const [memFile, setMemFile] = useState<File | null>(null);
  const [skillFile, setSkillFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    try {
      setAgents(await api.fetchAgents());
    } catch {
      /* backend not running */
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !memFile || !skillFile) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("name", name);
      fd.append("memory_file", memFile);
      fd.append("skills_file", skillFile);
      await api.createAgent(fd);
      setName("");
      setMemFile(null);
      setSkillFile(null);
      await load();
    } catch {
      alert("Upload failed — please check if the backend server is running.");
    }
    setLoading(false);
  };

  const handleDelete = async (id: number) => {
    await api.deleteAgent(id);
    await load();
  };

  return (
    <div>
      {/* Upload form */}
      <div className="card mb-32">
        <h3 className="section-title">🧬 Create New Player</h3>
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label>Player Name</label>
            <input
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Cyber Jordan"
            />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="form-group">
              <label>Memory File (.md)</label>
              <label className="file-drop">
                {memFile ? `✅ ${memFile.name}` : "Drag or click to select"}
                <input
                  type="file"
                  accept=".md"
                  style={{ display: "none" }}
                  onChange={(e) => setMemFile(e.target.files?.[0] || null)}
                />
              </label>
            </div>
            <div className="form-group">
              <label>Skills File (.md)</label>
              <label className="file-drop">
                {skillFile ? `✅ ${skillFile.name}` : "Drag or click to select"}
                <input
                  type="file"
                  accept=".md"
                  style={{ display: "none" }}
                  onChange={(e) => setSkillFile(e.target.files?.[0] || null)}
                />
              </label>
            </div>
          </div>
          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading || !name || !memFile || !skillFile}
          >
            {loading ? "Initializing..." : "⚡ Initialize Player"}
          </button>
        </form>
      </div>

      {/* Agent roster */}
      {agents.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🤖</div>
          <p>No agents yet. Upload memory and skills files to create your first player!</p>
        </div>
      ) : (
        <div className="card-grid">
          {agents.map((a) => (
            <AgentCard key={a.id} agent={a} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
