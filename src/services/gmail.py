from dataclasses import dataclass

import httpx
from httpx import HTTPError

from src.config import GmailConfig
from src.db.connector import AuthenticationConnector
from src.services.oauth import OAuthService
from src.services.schemas import (
    GmailListMessage,
    GmailListResponse,
    GmailMessage,
    GmailMessagePartBody,
)


@dataclass
class GmailAuthContext:
    access_token: str
    refresh_token: str
    expiry: int
    scopes: list[str]


class RetryableError(Exception): ...


class GmailConnector:
    def __init__(
        self,
        config: GmailConfig,
        auth_db: AuthenticationConnector,
        gmail_oauth: OAuthService,
    ):
        self.config = config
        self.auth_db = auth_db
        self.auth_ctx: GmailAuthContext | None = None
        self.gmail_oauth = gmail_oauth

    async def _get_auth_ctx(self, email: str) -> GmailAuthContext:
        auth_ctx = await self.auth_db.get(email)
        return GmailAuthContext(
            access_token=auth_ctx.access_token,
            refresh_token=auth_ctx.refresh_token,
            expiry=auth_ctx.expires_in,
            scopes=auth_ctx.scopes,
        )

    async def _make_request(
        self, email: str, endpoint: str, params: dict | None = None
    ):
        auth_ctx = await self._get_auth_ctx(email=email)
        header = {"Authorization": f"Bearer {auth_ctx.access_token}"}
        url = self.config.BASE_URL + endpoint
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=header, params=params)
            if response.status_code == 401:
                await self.gmail_oauth.refresh_token(email=email, config=self.config)
            if response.status_code != 200:
                raise HTTPError(
                    f"Gmail API error {response.status_code}: {response.text}"
                )
            return response.json()
        except Exception as e:
            raise HTTPError(f"Something went wrong: {e}")

    async def list_messages(
        self, last_successful_scan: str, email: str
    ) -> list[GmailListMessage]:
        # last_successful_scan is in the format YYYY/MM/DD
        endpoint = "/gmail/v1/users/me/messages"
        params = {"q": f"after:{last_successful_scan}", "includeSpamTrash": False}
        response = GmailListResponse.model_validate(
            await self._make_request(email=email, endpoint=endpoint, params=params)
        )
        gmail_messages = response.messages
        while response.nextPageToken:
            params["pageToken"] = response.nextPageToken
            response = GmailListResponse.model_validate(
                await self._make_request(email=email, endpoint=endpoint, params=params)
            )
            gmail_messages.extend(response.messages)

        return gmail_messages

    async def get_message(self, message_id: str, email: str) -> GmailMessage:
        # last_successful_scan is in the format YYYY/MM/DD
        endpoint = f"/gmail/v1/users/me/messages/{message_id}"
        response = await self._make_request(email=email, endpoint=endpoint)
        gmail_message = GmailMessage.model_validate(response)
        return gmail_message

    async def get_attachment(
        self, message_id: str, attachment_id: str, email: str
    ) -> GmailMessagePartBody:
        endpoint = (
            f"/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}"
        )
        response = await self._make_request(email=email, endpoint=endpoint)
        gmail_message = GmailMessagePartBody.model_validate(response)
        return gmail_message
