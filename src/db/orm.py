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
    scope: Mapped[list[str]]
    expires_in: Mapped[int]
    id: Mapped[str] = mapped_column(primary_key=True)


class User(Base):
    __tablename__ = "user"
    id: Mapped[str] = mapped_column(ForeignKey("authentication.id"))
    iss: Mapped[str]
    sub: Mapped[str]
    email: Mapped[str]
    email_verified: Mapped[bool]
    name: Mapped[str]
    given_name: Mapped[str]
    family_name: Mapped[str]
    picture: Mapped[str]
    locale: Mapped[str]
    iat: Mapped[int]
    exp: Mapped[int]
