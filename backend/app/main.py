from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.database import engine, Base, async_session
from app.models import User
from app.routes import agents, teams, matches
from sqlalchemy.future import select


async def lifespan(app: FastAPI):
    # Create tables on startup (fine for dev; use Alembic for prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed a default user for MVP (no auth yet)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == 1))
        if not result.scalar_one_or_none():
            session.add(User(username="default_player"))
            await session.commit()

    yield
    await engine.dispose()


app = FastAPI(
    title="Virtual Hoops API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(matches.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"service": "Virtual Hoops API", "version": "2.0.0"}
