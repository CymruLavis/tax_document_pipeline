from dataclasses import dataclass

import httpx
from fastapi import Depends
from httpx import HTTPError

from src.config import GmailConfig
from src.dependancies import get_gmail_config
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


class GmailConnector:
    def __init__(self, config: GmailConfig = Depends(get_gmail_config)):
        self.config = config
        self.auth_ctx: GmailAuthContext | None = None

    async def _get_auth_ctx(self) -> GmailAuthContext:
        if self.auth_ctx:
            return self.auth_ctx
        return GmailAuthContext(
            access_token="", refresh_token="", expiry=123, scopes=[]
        )
        # get auth context from database or something

    async def _make_request(self, endpoint: str, params: dict | None = None):
        auth_ctx = await self._get_auth_ctx()
        header = {"Authorization": f"Bearer {auth_ctx.access_token}"}
        url = self.config.BASE_URL + endpoint
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=header, params=params)
            if response.status_code != 200:
                raise HTTPError(
                    f"Gmail API error {response.status_code}: {response.text}"
                )
            return response.json()
        except Exception as e:
            raise HTTPError(f"Something went wrong: {e}")

    async def list_messages(self, last_successful_scan: str) -> list[GmailListMessage]:
        # last_successful_scan is in the format YYYY/MM/DD
        endpoint = "/gmail/v1/users/me/messages"
        params = {"q": "after:2026/06/01", "includeSpamTrash": False}
        response = GmailListResponse.model_validate(
            await self._make_request(endpoint=endpoint, params=params)
        )
        gmail_messages = response.messages
        while response.nextPageToken:
            params["pageToken"] = response.nextPageToken
            response = GmailListResponse.model_validate(
                await self._make_request(endpoint=endpoint, params=params)
            )
            gmail_messages.extend(response.messages)

        return gmail_messages

    async def get_message(self, message_id: str) -> GmailMessage:
        # last_successful_scan is in the format YYYY/MM/DD
        endpoint = f"/gmail/v1/users/me/messages/{message_id}"
        response = await self._make_request(endpoint=endpoint)
        gmail_message = GmailMessage.model_validate(response)
        return gmail_message

    async def get_attachment(
        self, message_id: str, attachment_id: str
    ) -> GmailMessagePartBody:
        endpoint = (
            f"/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}"
        )
        response = await self._make_request(endpoint=endpoint)
        gmail_message = GmailMessagePartBody.model_validate(response)
        return gmail_message
