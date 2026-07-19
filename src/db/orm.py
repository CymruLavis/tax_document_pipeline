from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    # Creating a Base class syncs up the metadata for all child classes created.
    # If each created class inheritted from DeclarativeBase then they would
    # have separate metadata registries
    pass


class Authentication(Base):
    __tablename__ = "authentication"

    provider: Mapped[str]
    access_token: Mapped[str]
    refresh_token: Mapped[str]
    scopes: Mapped[list[str]]
    expires_in: Mapped[int]
    email: Mapped[str]
    id: Mapped[UUID] = mapped_column(primary_key=True)


class Email(Base):
    __tablename__ = "email"
    id: Mapped[str] = mapped_column(primary_key=True)
    provider: Mapped[str]
    subject: Mapped[str]
    sender_name: Mapped[str]
    sender_email: Mapped[str]
    recieved_at: Mapped[datetime]
    body_text: Mapped[str]
    receipt_ids: Mapped[list[str]]
    file_destination: Mapped[str]


class ReceiptDetail(Base):
    __tablename__ = "recepit_detail"
    id: Mapped[str] = mapped_column(primary_key=True)
    email_id: Mapped[str] = mapped_column(ForeignKey("email.id"))
    vendor: Mapped[str]
    total_cost: Mapped[float]
    date_of_transaction: Mapped[datetime]


class State(Base):
    __tablename__ = "state"
    user_email: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    last_sync: Mapped[datetime]
    status: Mapped[str]
