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
    last_successful_scan = "2026/06/20"
    messages = await gmail_client.list_messages(
        last_successful_scan=last_successful_scan
    )
    assert len(messages) > 0
    print(messages[0])
    print(len(messages))


@pytest.mark.asyncio
async def test_get_messages(gmail_client):
    message_id = "19ee7cb27153ca56"
    message = await gmail_client.get_message(message_id=message_id)
    assert message
    # print(message.threadId)
    # print(message.internalDate)
    headers = {h.name.lower(): h.value for h in message.payload.headers}
    subject = headers.get("subject")
    sender = headers.get("from")
    recipient = headers.get("to")
    date = headers.get("date")
    message_id = headers.get("message-id")
    print("HEADERS")
    print(
        f"subject:{subject}\nsender:{sender}\nrecipient:{recipient}\ndate:{date}\nmessage_id:{message_id}"
    )


def detect_type(raw_bytes: bytes):
    if raw_bytes.startswith(b"%PDF"):
        return "pdf"
    if raw_bytes.startswith(b"PK"):
        return "zip/docx"
    if raw_bytes.startswith(b"\xff\xd8"):
        return "jpg"
    return "unknown"


@pytest.mark.asyncio
async def test_get_attachment(gmail_client):
    message_id = "19ee7cb27153ca56"
    attachment_id = "ANGjdJ8CnIU_n3uxuovmyg4rnkuQ8tkh1QtwrkJIeI7B6nAF2xX4sXSbkXtfXyoBzmmKoW8Fkj21Nf_YK6SvnNLa5rkocvW2aewBciOHYrVdAaRdPHBPe-wdpdUgEsfQ7s4au9rROZZOOkEIfW2Zxmo5GHdJuO_N52ZI62EMhMum9lDfZpnPd_QKaArdYuLKXSR7N5FHNy5c5-se93WVKabIEpczDkcZz5nZydEQ9qQ9_36AIQoi6S2URIGKkpDH3dPSaG7oZpBCDcbqLjn3GA_qi21Y5UJQ5DMa2JmdfZK78wdVr-dN5eFJYTv-bucngNMWfdqNnoDxb26i0R0mjqFHoCghWTZf5deZzUy3o0_VInYRdkUeS7a02eu2RvN-akRSHoYBTW_vvIHVrGhH"
    attachment = await gmail_client.get_attachment(
        message_id=message_id, attachment_id=attachment_id
    )
    assert attachment
    print(f"ID: {attachment.attachmentId}")
    print(f" SIZE: {attachment.size}")
    data = attachment.data
    if data:
        raw_bytes = base64.urlsafe_b64decode(data)
        file_type = detect_type(raw_bytes=raw_bytes)
        print(file_type)

        import fitz

        doc = fitz.open(stream=raw_bytes, filetype="pdf")
        pages = []
        for page in doc:
            text = page.get_text("text")
            if text:
                pages.append(text)

        print("\n".join(pages))
