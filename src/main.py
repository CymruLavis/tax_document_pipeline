from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app_state import AppContext
from src.db.database import engine, session_factory


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.context = AppContext(session_factory=session_factory, engine=engine)

    yield
    await app.state.context.engine.dispose()


app = FastAPI(lifespan=lifespan)
