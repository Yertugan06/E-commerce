from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.features.auth.router import router as auth_router
from app.features.users.models import User


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        await create_db_and_tables()
    except Exception:
        pass
    yield


app = FastAPI(title="E-Commerce MVP", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"status": "ok"}
