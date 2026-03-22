# Contributing to Agentic Sports Simulation

We're excited that you want to contribute to the **Agentic Sports Simulation** project! Here's how you can get started.

## 🌟 Ways to Contribute
There are many ways to contribute beyond writing code:
- **Scouting**: Creating and uploading new agent profiles (Markdown files) to enrich the player roster.
- **Coaching**: Improving the simulation parameters and player logic in the `game_engine.py`.
- **Engineering**: Enhancing the backend API, frontend UI, or integration with new sports.
- **Reporting**: Finding and reporting bugs.

## 🛠️ Development Setup

#### 1. Fork and Clone
```bash
git clone https://github.com/Douglashwang82/Agentic-Sports-Simulation.git
cd Agentic-Sports-Simulation
```

#### 2. Install the Core Library
```bash
pip install -e .
```

#### 3. Web App Reference Implementation (Python/FastAPI)
- Navigate to the backend: `cd examples/web_app/backend`
- Create a virtual environment: `python -m venv venv`
- Install dependencies: `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.
- Start the server: `uvicorn app.main:app --reload`

#### 4. Web App UI (TypeScript/React/Vite)
- Navigate to the frontend: `cd examples/web_app/frontend`
- Install dependencies: `npm install`
- Start the dev server: `npm run dev`

## 📜 Coding Guidelines

- **Style**: Follow PEP 8 for Python and use Prettier/ESLint for TypeScript.
- **Modularity**: Keep the `agentic_sports` core library framework-agnostic. Use callbacks for any external side effects (like Redis or UI logging).
- **Testing**: We appreciate tests! Add them to `tests/` if possible.

## 📬 Pull Request Process

1. Create a descriptive branch: `git checkout -b feature/your-feature-name`.
2. Commit changes with clear, concise messages.
3. Push to your branch and open a Pull Request.
4. Ensure your code passes any existing linting and build checks.

## ⚖️ License
By contributing, you agree that your contributions will be licensed under the project's **MIT License**.

---

Thank you for helping us build the future of agentic sports!
