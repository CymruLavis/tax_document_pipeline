from google.auth.transport import requests
from google.oauth2 import id_token
from httpx import AsyncClient, HTTPStatusError, RequestError, Response, TimeoutException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    AccessTokenResponse,
    OAuthError,
    OAuthRequestError,
    OAuthStatusError,
    OAuthTimeoutError,
)
from src.config import GmailConfig
from src.db.connector import AuthenticationConnector
from src.db.context import AuthContext


class OAuthService:
    def __init__(
        self, client: AsyncClient, _oauth_connector: AuthenticationConnector
    ) -> None:
        self._client = client
        self.oauth_connector = _oauth_connector

    async def _make_request(self, url: str, data: dict) -> Response:
        async with self._client as client:
            try:
                response = await client.post(url=url, data=data)
                response.raise_for_status()
                return response
            except TimeoutException as e:
                raise OAuthTimeoutError("Request timed out after") from e
            except RequestError as e:
                raise OAuthRequestError("Failed to connect to OAuth provider") from e
            except HTTPStatusError as e:
                raise OAuthStatusError(
                    f"OAuth provider returned {e.response.status_code}"
                ) from e
            except Exception as e:
                raise OAuthError("Unhandled Error") from e

    async def _extract_email_from_token_id(
        self, id_token_str: str, client_id: str
    ) -> str:
        claims = id_token.verify_oauth2_token(
            id_token_str, requests.Request(), client_id
        )
        return claims["email"]

    async def get_access_token(
        self, code: str, config: GmailConfig, session: AsyncSession
    ) -> Response:
        data = {
            "code": code,
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "redirect_uri": config.REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_response = await self._make_request(url=config.TOKEN_URL, data=data)
        _auth = AccessTokenResponse(**token_response.json())
        if _auth.refresh_token is None:
            raise OAuthError("No refresh token returned in initail token fetch")

        auth = AuthContext(
            provider="gmail",
            access_token=_auth.access_token,
            refresh_token=_auth.refresh_token,
            scopes=_auth.scope.split(" "),
            email=await self._extract_email_from_token_id(
                _auth.id_token, config.CLIENT_ID
            ),
            expires_in=_auth.expires_in,
        )
        await self.oauth_connector.add(session=session, auth=auth)
        await session.commit()
        return token_response

    async def refresh_token(
        self, email: str, session: AsyncSession, config: GmailConfig
    ) -> Response:
        auth = await self.oauth_connector.get_auth_by_email(
            session=session, email=email
        )
        data = {
            "grant_type": "refresh_token",
            "refresh_token": auth.refresh_token,
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
        }
        token_response = await self._make_request(url=config.TOKEN_URL, data=data)
        _auth = AccessTokenResponse(**token_response.json())
        new_auth = AuthContext(
            provider=auth.provider,
            access_token=_auth.access_token,
            refresh_token=auth.refresh_token,
            scopes=_auth.scope.split(" "),
            expires_in=_auth.expires_in,
            email=auth.email,
            id=auth.id,
        )
        await self.oauth_connector.update(session=session, auth=new_auth)
        await session.commit()
        return token_response
