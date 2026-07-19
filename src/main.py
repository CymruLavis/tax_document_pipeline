from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI
from httpx import AsyncClient, Timeout
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.config import GmailConfig
from src.db.connector import AuthenticationConnector
from src.db.database import engine, session_factory
from src.services.oauth import OAuthService


@dataclass(slots=True)
class AppContext:
    session_factory: async_sessionmaker[AsyncSession]
    engine: AsyncEngine
    gmail_config: GmailConfig
    oauth_service: OAuthService
    oauth_connector: AuthenticationConnector


@asynccontextmanager
async def lifespan(app: FastAPI):
    oauth_timeout = Timeout(connect=5.0, write=10.0, read=10.0, pool=5.0)
    oauth_connector = AuthenticationConnector()
    oauth_client = AsyncClient(timeout=oauth_timeout)
    oauth_service = OAuthService(client=oauth_client, _oauth_connector=oauth_connector)
    app.state.context = AppContext(
        session_factory=session_factory,
        engine=engine,
        gmail_config=GmailConfig(),  # pyright: ignore
        oauth_service=oauth_service,
        oauth_connector=oauth_connector,
    )

    yield
    await app.state.context.engine.dispose()


app = FastAPI(lifespan=lifespan)
