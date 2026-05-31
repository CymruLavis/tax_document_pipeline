from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from src.config import GmailConfig

oauth = FastAPI()
config = GmailConfig() # type: ignore


@oauth.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2> Welcome to FastAPI</h2>
    <a href="/oauth/authorize"> Login with Google</a>
    """


@oauth.post("/oauth/authorize")
def authorize():
    query_params = {
        "client_id": config.CLIENT_ID,
        "redirect_uri": config.REDIRECT_URI,
        "response_type": "code",
        "scope": "email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{config.AUTH_URL}?{urlencode(query_params)}"
    return RedirectResponse(url)


@oauth.get("/auth/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    data = {
        "code": code,
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET,
        "redirect_uri": config.REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(config.TOKEN_URL, data=data)

    return JSONResponse(content={
        "status": token_response.status_code,
        "body": token_response.text
    })