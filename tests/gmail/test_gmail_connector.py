import base64

import pytest
from dotenv import load_dotenv

from src.config import GmailConfig
from src.services.gmail import GmailConnector

load_dotenv()


@pytest.fixture
def gmail_config():
    return GmailConfig()  # type: ignore


@pytest.fixture
def gmail_client(gmail_config):
    return GmailConnector(config=gmail_config)


@pytest.mark.asyncio
async def test_list_messages(gmail_client):
    last_successful_scan = "2026/06/05"
    messages = await gmail_client.list_messages(
        last_successful_scan=last_successful_scan
    )
    assert len(messages) > 0
    print(messages[0])
    print(len(messages))


@pytest.mark.asyncio
async def test_get_messages(gmail_client):
    message_id = "19ea303a7a1d2517"
    message = await gmail_client.get_message(message_id=message_id)
    assert message
    decoded_message = base64.urlsafe_b64decode(
        message.payload.body.data.encode("utf-8")
    ).decode("utf-8")
    print(f"BODY: {decoded_message}")