import { useState } from "react";
import AgentsPanel from "./components/AgentsPanel";
import TeamsPanel from "./components/TeamsPanel";
import ArenaPanel from "./components/ArenaPanel";
import "./index.css";

const TABS = [
  { key: "agents", label: "🤖 Agents" },
  { key: "teams", label: "🛡️ Teams" },
  { key: "arena", label: "🏟️ Arena" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function App() {
  const [tab, setTab] = useState<TabKey>("agents");

  return (
    <div className="shell">
      <header className="hero">
        <h1>Virtual League</h1>
        <p>The premier AI agent sports simulation platform</p>
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
