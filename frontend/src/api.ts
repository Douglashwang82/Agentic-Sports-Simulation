const API_BASE = "http://localhost:8000/api/v1";
const WS_BASE = "ws://localhost:8000/api/v1";

export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

export async function createAgent(formData: FormData) {
  const res = await fetch(`${API_BASE}/agents`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to create agent");
  return res.json();
}

export async function deleteAgent(id: number) {
  const res = await fetch(`${API_BASE}/agents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete agent");
  return res.json();
}

export async function fetchTeams() {
  const res = await fetch(`${API_BASE}/teams`);
  if (!res.ok) throw new Error("Failed to fetch teams");
  return res.json();
}

export async function createTeam(name: string, agentIds: number[]) {
  const res = await fetch(`${API_BASE}/teams`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, agent_ids: agentIds }),
  });
  if (!res.ok) throw new Error("Failed to create team");
  return res.json();
}

export async function deleteTeam(id: number) {
  const res = await fetch(`${API_BASE}/teams/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete team");
  return res.json();
}

export async function fetchMatches() {
  const res = await fetch(`${API_BASE}/matches`);
  if (!res.ok) throw new Error("Failed to fetch matches");
  return res.json();
}

export async function createMatch(homeTeamId: number, awayTeamId: number) {
  const res = await fetch(`${API_BASE}/matches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ home_team_id: homeTeamId, away_team_id: awayTeamId }),
  });
  if (!res.ok) throw new Error("Failed to create match");
  return res.json();
}

export async function startMatch(matchId: number) {
  const res = await fetch(`${API_BASE}/matches/${matchId}/start`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to start match");
  return res.json();
}

export function createMatchStream(matchId: number): WebSocket {
  return new WebSocket(`${WS_BASE}/matches/${matchId}/stream`);
}
