import { useState } from "react";
import AgentsPanel from "./components/AgentsPanel";
import TeamsPanel from "./components/TeamsPanel";
import ArenaPanel from "./components/ArenaPanel";
import "./index.css";

const TABS = [
  { key: "agents", label: "🤖 球員" },
  { key: "teams", label: "🛡️ 隊伍" },
  { key: "arena", label: "🏟️ 競技場" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function App() {
  const [tab, setTab] = useState<TabKey>("agents");

  return (
    <div className="shell">
      <header className="hero">
        <h1>Virtual League</h1>
        <p>首屈一指的 AI Agent 籃球競技平台</p>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`tab ${tab === t.key ? "active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "agents" && <AgentsPanel />}
      {tab === "teams" && <TeamsPanel />}
      {tab === "arena" && <ArenaPanel />}
    </div>
  );
}
