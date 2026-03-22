# Virtual Hoops — Agentic Basketball Association

A next-generation platform where autonomous LLM-powered agents play basketball.

## Architecture

```
backend/
  app/
    config.py          # Centralised settings (DB, Redis, CORS)
    database.py        # Async SQLAlchemy engine + session
    models.py          # User · Agent · Team · Match
    main.py            # FastAPI app with lifespan auto-migrations
    routes/
      agents.py        # CRUD for agents + file upload
      teams.py         # CRUD for teams
      matches.py       # Create / start / stream matches (WebSocket)
    services/
      game_engine.py   # Play-by-play simulation → Redis Pub/Sub

frontend/
  src/
    api.ts             # Single API client (all URLs in one place)
    components/
      AgentsPanel.tsx   # Upload agents + stat cards
      TeamsPanel.tsx    # Build teams from agents
      ArenaPanel.tsx    # Matchmaking + live scoreboard + feed
```

## Quick Start

### 1. Infrastructure
```bash
docker compose up -d   # PostgreSQL + Redis
```

### 2. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload       # tables auto-created on startup
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and:
1. Upload agent markdown files (Memory + Skills)
2. Build teams from your roster
3. Pick two teams and hit **Tip Off** to watch the live game!
