from fastapi import Depends, Request

from src.config import GmailConfig
from src.context import AppContext
from src.services.oauth import OAuthService


def get_context(request: Request) -> AppContext:
    return request.app.state.context


async def get_gmail_config(context: AppContext = Depends(get_context)) -> GmailConfig:
    return context.gmail_config


async def get_oauth_service(context: AppContext = Depends(get_context)) -> OAuthService:
    return context.oauth_service
