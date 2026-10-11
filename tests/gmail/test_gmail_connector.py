from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.config import GmailConfig
from src.db.context import AuthContext
from src.db.connector import AuthenticationConnector
import src.services.gmail as gmail_module
from src.services.gmail import GmailConnector


@pytest.fixture
def gmail_config():
    return GmailConfig(
        CLIENT_ID="test-client-id",
        CLIENT_SECRET="test-client-secret",
        TOKEN_URL="https://example.test/token",
        REDIRECT_URI="https://example.test/callback",
        BASE_URL="https://gmail.googleapis.test",
        AUTH_URL="https://example.test/auth",
        SCOPES=["mail.readonly"],
    )


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one.return_value = AuthContext(
        provider="gmail",
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        scopes=["mail.readonly"],
        expires_in=3600,
        email="tester@example.test",
    )
    session.execute.return_value = result

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=session)
    session_context.__aexit__ = AsyncMock(return_value=False)
    session_factory = MagicMock()
    session_factory.begin.return_value = session_context

    return {"session": session, "session_factory": session_factory}


@pytest.fixture
def auth_connector(mock_db_session):
    return AuthenticationConnector(
        session_factory=mock_db_session["session_factory"]
    )


@pytest.fixture
def gmail_api_service(monkeypatch):
    responses = {}
    requests = []

    def handle_request(request):
        requests.append(request)
        page_token = request.url.params.get("pageToken")
        payload = responses.get((request.url.path, page_token))
        if payload is None:
            return httpx.Response(404, json={"error": "No mock response"})
        return httpx.Response(200, json=payload)

    original_async_client = httpx.AsyncClient
    transport = httpx.MockTransport(handle_request)
    monkeypatch.setattr(
        gmail_module.httpx,
        "AsyncClient",
        lambda: original_async_client(transport=transport),
    )
    return responses, requests


@pytest.fixture
def gmail_client(gmail_config, auth_connector):
    return GmailConnector(config=gmail_config, auth_db=auth_connector)


@pytest.mark.asyncio
async def test_gmail_config_load(gmail_config):
    assert gmail_config.BASE_URL == "https://gmail.googleapis.test"


@pytest.mark.asyncio
async def test_list_messages(gmail_client, gmail_api_service, mock_db_session):
    responses, requests = gmail_api_service
    path = "/gmail/v1/users/me/messages"
    responses[(path, None)] = {
        "messages": [{"id": "message-1", "threadId": "thread-1"}],
        "nextPageToken": "next-page",
        "resultSizeEstimate": 2,
    }
    responses[(path, "next-page")] = {
        "messages": [{"id": "message-2", "threadId": "thread-2"}],
        "resultSizeEstimate": 1,
    }

    messages = await gmail_client.list_messages(
        email="tester@example.test", last_successful_scan="2026/06/20"
    )
    assert [message.id for message in messages] == ["message-1", "message-2"]
    assert len(requests) == 2
    assert requests[0].headers["Authorization"] == "Bearer test-access-token"
    assert requests[1].url.params["pageToken"] == "next-page"
    mock_db_session["session"].execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_message(gmail_client, gmail_api_service):
    responses, _ = gmail_api_service
    message_id = "message-1"
    responses[(f"/gmail/v1/users/me/messages/{message_id}", None)] = {
        "id": message_id,
        "threadId": "thread-1",
        "labelIds": ["INBOX"],
        "snippet": "Test message",
        "historyId": "history-1",
        "internalDate": "1781913600000",
        "payload": {
            "partId": "0",
            "mimeType": "text/plain",
            "filename": "",
            "headers": [],
            "body": {"size": 0},
        },
        "sizeEstimate": 0,
    }

    message = await gmail_client.get_message(
        email="tester@example.test", message_id=message_id
    )

    assert message.id == message_id
    assert message.payload.mimeType == "text/plain"


@pytest.mark.asyncio
async def test_get_attachment(gmail_client, gmail_api_service):
    responses, _ = gmail_api_service
    message_id = "message-1"
    attachment_id = "attachment-1"
    responses[
        (
            f"/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}",
            None,
        )
    ] = {"attachmentId": attachment_id, "size": 7, "data": "cGF5bG9hZA=="}

    attachment = await gmail_client.get_attachment(
        email="tester@example.test",
        message_id=message_id,
        attachment_id=attachment_id,
    )

    assert attachment.attachmentId == attachment_id
    assert attachment.data == "cGF5bG9hZA=="
