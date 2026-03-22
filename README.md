<p align="center">
  <img src="./logo.png" width="400" alt="Agentic Sports Simulation Logo">
</p>

# 🏀 Agentic Sports Simulation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Generative AI](https://img.shields.io/badge/AI-Gemini%20Pro-4285F4.svg?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

A next-generation sports simulation platform where **autonomous LLM-powered agents** compete in various sports. In this simulation, players aren't just stats; they have personalities, memories of past games, and unique skills that dictate their decision-making on the field.

---

## ✨ Key Features

- **🧠 Agentic Decision Making**: Every play is driven by LLMs. Players decide whether to shoot, pass, or drive based on their personality and game context.
- **📜 Persistent Memory**: Agents remember their successes and failures. A player might shy away from a defender who blocked them earlier or get "in the zone" after a hot streak.
- **⚡ Real-time Simulation**: Watch games live via WebSockets with a play-by-play feed and dynamic scoreboard.
- **🛠️ Fully Customizable**: Write your own player profiles in Markdown and watch them come to life.
- **🏗️ Modern Tech Stack**: Built with FastAPI, PostgreSQL, Redis, and React.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Docker & Docker Compose**
- **Python 3.10+**
- **Node.js 18+**
- **Google Gemini API Key** (Set in `.env`)

### 2. Infrastructure Setup
Spin up the database and message broker:
```bash
docker compose up -d
```

### 3. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Set your DATABASE_URL and GEMINI_API_KEY in backend/.env
uvicorn app.main:app --reload
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173` to start your first Tip-Off!

---

## ⛹️ How to Create & Upload Your Own Agent

Developing for the Agentic Sports Simulation is designed to be extensible. You can "scout" and upload new talent by creating two simple Markdown files for each agent.

### 1. Define Skills (`skills.md`)
Specify the physical and technical attributes of your player.
```markdown
# Agent Skills & Attributes
## Physical Attributes (1-99)
- Speed: 88
- Strength: 65
- Stamina: 92

## Technical Skills (1-99)
- 3PT Shooting: 85
- Mid-Range: 90
- Playmaking / Passing: 98
- Perimeter Defense: 75

## Special Badges (Traits)
1. **[Dime Dropper]**: Boosts teammate shot success on open passes.
2. **[Clutch Gene]**: Performance increases in the final 2 minutes.
```

### 2. Define Personality (`memory.md`)
Tell the story of your player and how they behave.
```markdown
# Agent Memory Context
- **Name**: "The General"
- **Personality**: Extremely calm, team-first mentality.
- **Past Experiences**:
  - Once led a 10-point comeback via Pick & Roll.
  - Tends to use pump fakes against aggressive defenders.
```

### 3. Upload via Dashboard
Head to the **Agents** tab in the web UI, click **Upload**, and select your files. The system will automatically parse them and add the player to your roster.

---

## 🏗️ Project Architecture

```text
├── backend/
│   ├── app/
│   │   ├── models.py          # Database Schema (SQLAlchemy)
│   │   ├── routes/            # REST API endpoints
│   │   ├── services/          # Basketball Engine & LLM Logic
│   │   └── database.py        # Connection Management
├── frontend/
│   ├── src/
│   │   ├── components/        # Arena, Roster, and Admin UI
│   │   └── api.ts             # Typed API client
└── docker-compose.yml         # Dev Environment (Postgres, Redis)
```

---

## 🤝 Contributing

We welcome scouts, coaches, and developers to join the ABA!
1. **Fork** the repository.
2. Create a **Feature Branch** (`git checkout -b feature/AmazingFeature`).
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
4. **Push** to the Branch (`git push origin feature/AmazingFeature`).
5. Open a **Pull Request**.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">Built with ❤️ by the <a href="https://github.com/Douglashwang82/Agentic-Sports-Simulation">Agentic Sports Community</a></p>
