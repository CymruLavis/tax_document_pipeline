from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine

from src.config import GmailConfig
from src.db.connector import AuthenticationConnector
from src.services.oauth import OAuthService


@dataclass(slots=True, frozen=True)
class AppContext:
    engine: AsyncEngine
    gmail_config: GmailConfig
    oauth_service: OAuthService
    oauth_connector: AuthenticationConnector
