from pydantic import BaseModel, Field


class GmailClassificationLabelFieldValue(BaseModel):
    fieldId: str
    selection: str


class GmailClassificationLabelValue(BaseModel):
    labelId: str
    fields: list[GmailClassificationLabelFieldValue]


class GmailHeader(BaseModel):
    name: str
    value: str


class GmailMessagePartBody(BaseModel):
    attachmentId: str | None = None
    size: int
    data: str


class GmailMessagePart(BaseModel):
    partId: str
    mimeType: str
    filename: str
    headers: list[GmailHeader]
    body: GmailMessagePartBody
    parts: list["GmailMessagePart"] = Field(default_factory=list)


class GmailMessage(BaseModel):
    id: str
    threadId: str
    labelIds: list[str]
    snippet: str
    historyId: str
    internalDate: str
    payload: GmailMessagePart
    sizeEstimate: int
    raw: str | None = None
    classificationLabelValues: GmailClassificationLabelValue | None = None


class GmailListMessage(BaseModel):
    id: str
    threadId: str


class GmailListResponse(BaseModel):
    messages: list[GmailListMessage]
    nextPageToken: str | None = None
    resultSizeEstimate: int
