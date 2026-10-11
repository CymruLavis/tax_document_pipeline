from fastapi import FastAPI

from src.services.schemas import GmailListMessage, GmailMessage, GmailMessagePartBody

gmail = FastAPI()


@gmail.get("/list_messages")
async def list_messages() -> list[GmailListMessage]: ...


@gmail.get("/get_message/{message_id}")
async def get_message() -> list[GmailMessage]: ...


@gmail.get("/get_attachment/{attachment_id}")
async def get_attachment() -> list[GmailMessagePartBody]: ...
