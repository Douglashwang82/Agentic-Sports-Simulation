import "./AgentCard.css";

export interface AgentData {
  id: number;
  name: string;
  avatar_emoji: string;
  shooting: number;
  defense: number;
  passing: number;
  speed: number;
  stamina: number;
}

/* Deterministic colour palette from name hash */
const PALETTES = [
  ["#f97316", "#fbbf24"],
  ["#3b82f6", "#06b6d4"],
  ["#a855f7", "#ec4899"],
  ["#22c55e", "#14b8a6"],
  ["#ef4444", "#f97316"],
  ["#6366f1", "#8b5cf6"],
  ["#0ea5e9", "#22d3ee"],
  ["#e11d48", "#f43f5e"],
];

function hashName(name: string) {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function StatBar({ label, value, color }: { label: string; value: number; color: string }) {
  const tier =
    value >= 85 ? "S" : value >= 70 ? "A" : value >= 55 ? "B" : value >= 40 ? "C" : "D";
  return (
    <div className="ac-stat">
      <span className="ac-stat-label">{label}</span>
      <div className="ac-stat-track">
        <div className="ac-stat-fill" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className={`ac-stat-tier tier-${tier}`}>{value}</span>
    </div>
  );
}

interface Props {
  agent: AgentData;
  onDelete?: (id: number) => void;
  compact?: boolean;
}

export default function AgentCard({ agent, onDelete, compact }: Props) {
  const palette = PALETTES[hashName(agent.name) % PALETTES.length];
  const gradientBg = `linear-gradient(135deg, ${palette[0]}22, ${palette[1]}22)`;
  const accentColor = palette[0];

  const stats = [
    { label: "SHT", value: agent.shooting },
    { label: "DEF", value: agent.defense },
    { label: "PAS", value: agent.passing },
    { label: "SPD", value: agent.speed },
    { label: "STA", value: agent.stamina },
  ];

  const overall = Math.round(stats.reduce((s, v) => s + v.value, 0) / stats.length);

  return (
    <div className={`ac ${compact ? "ac--compact" : ""}`} style={{ background: gradientBg }}>
      {onDelete && (
        <button className="ac-delete" onClick={() => onDelete(agent.id)} title="Delete Agent">
          ✕
        </button>
      )}

      {/* ─── Avatar / Photo Area ─── */}
      <div className="ac-avatar" style={{ background: `linear-gradient(135deg, ${palette[0]}, ${palette[1]})` }}>
        <span className="ac-avatar-emoji">{agent.avatar_emoji}</span>
      </div>

      {/* ─── Name + Overall ─── */}
      <div className="ac-header">
        <h3 className="ac-name">{agent.name}</h3>
        <div className="ac-overall" style={{ borderColor: accentColor, color: accentColor }}>
          {overall}
        </div>
      </div>

      {/* ─── Skills ─── */}
      <div className="ac-stats">
        {stats.map((s) => (
          <StatBar key={s.label} label={s.label} value={s.value} color={accentColor} />
        ))}
      </div>
    </div>
  );
}
