from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.base import Base
from .db.session import engine
from .api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Auth Service",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
