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
      alert("上傳失敗 — 請確認後端伺服器是否已啟動。");
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
        <h3 className="section-title">🧬 建立新球員</h3>
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label>球員名稱</label>
            <input
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="例：賽博喬丹"
            />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="form-group">
              <label>記憶檔案 (.md)</label>
              <label className="file-drop">
                {memFile ? `✅ ${memFile.name}` : "拖曳或點擊選擇檔案"}
                <input
                  type="file"
                  accept=".md"
                  style={{ display: "none" }}
                  onChange={(e) => setMemFile(e.target.files?.[0] || null)}
                />
              </label>
            </div>
            <div className="form-group">
              <label>技能檔案 (.md)</label>
              <label className="file-drop">
                {skillFile ? `✅ ${skillFile.name}` : "拖曳或點擊選擇檔案"}
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
            {loading ? "初始化中…" : "⚡ 初始化球員"}
          </button>
        </form>
      </div>

      {/* Agent roster */}
      {agents.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🤖</div>
          <p>目前沒有球員。上傳記憶和技能檔案來建立你的第一位 AI 球員吧！</p>
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
