from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient, Limits, Timeout

from src.api.oauth import oauth
from src.config import GmailConfig
from src.context import AppContext
from src.db.connector import AuthenticationConnector
from src.db.database import engine, session_factory
from src.db.orm import Base
from src.services.oauth import OAuthService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    http_timeout = Timeout(connect=5.0, write=10.0, read=10.0, pool=5.0)
    http_limits = Limits(
        max_connections=100, max_keepalive_connections=20, keepalive_expiry=5.0
    )
    oauth_connector = AuthenticationConnector(session_factory=session_factory)
    oauth_client = AsyncClient(timeout=http_timeout, limits=http_limits)
    oauth_service = OAuthService(client=oauth_client, _oauth_connector=oauth_connector)
    app.state.context = AppContext(
        engine=engine,
        gmail_config=GmailConfig(),  # pyright: ignore
        oauth_service=oauth_service,
        oauth_connector=oauth_connector,
    )

    yield
    await oauth_client.aclose()
    await app.state.context.engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(oauth)
