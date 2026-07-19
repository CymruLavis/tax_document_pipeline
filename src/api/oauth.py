from urllib.parse import urlencode

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import GmailConfig
from src.dependancies import get_db_session, get_gmail_config, get_oauth_service
from src.services.oauth import OAuthService

oauth = FastAPI()


@oauth.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2> Welcome to FastAPI</h2>
    <a href="/oauth/authorize"> Login with Google</a>
    """


@oauth.get("/oauth/authorize")
def authorize(config: GmailConfig = Depends(get_gmail_config)) -> RedirectResponse:
    query_params = {
        "client_id": config.CLIENT_ID,
        "redirect_uri": config.REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(config.SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    url = f"{config.AUTH_URL}?{urlencode(query_params)}"
    return RedirectResponse(url)


@oauth.get("/auth/callback")
async def callback(
    code: str,
    config: GmailConfig = Depends(get_gmail_config),
    oauth_service: OAuthService = Depends(get_oauth_service),
    db_session: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")
    token_response = await oauth_service.get_access_token(
        code=code, config=config, session=db_session
    )

    return JSONResponse(
        content={"status": token_response.status_code, "body": token_response.text}
    )


@oauth.post("/auth/refresh")
async def refresh(
    email: str,
    config: GmailConfig = Depends(get_gmail_config),
    oauth_service: OAuthService = Depends(get_oauth_service),
    db_session: AsyncSession = Depends(get_db_session),
) -> JSONResponse:

    token_response = await oauth_service.refresh_token(
        email=email, config=config, session=db_session
    )

    return JSONResponse(
        content={"status": token_response.status_code, "body": token_response.text}
    )
