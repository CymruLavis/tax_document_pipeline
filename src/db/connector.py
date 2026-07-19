from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.context import AuthContext, EmailContext, ReceiptContext
from src.db.orm import Authentication, Email, ReceiptDetail


class AuthenticationConnector:
    async def add(self, session: AsyncSession, auth: AuthContext) -> None:
        stmt = insert(Authentication).values(**auth.model_dump())
        await session.execute(stmt)

    async def get(self, session: AsyncSession, id: UUID) -> AuthContext:
        stmt = select(Authentication).where(Authentication.id == id)
        rows = await session.execute(stmt)
        result = rows.scalar_one()
        return AuthContext.model_validate(result)

    async def delete(self, session: AsyncSession, id: UUID) -> None:
        stmt = delete(Authentication).where(Authentication.id == id)
        await session.execute(stmt)

    async def update(self, session: AsyncSession, auth: AuthContext) -> None:
        stmt = (
            update(Authentication)
            .where(Authentication.id == auth.id)
            .values(**auth.model_dump())
        )
        await session.execute(stmt)

    async def get_auth_by_email(self, session: AsyncSession, email: str) -> AuthContext:
        stmt = select(Authentication).where(Authentication.email == email)
        rows = await session.execute(stmt)
        result = rows.scalar_one()
        return AuthContext.model_validate(result)


class EmailConnector:
    async def add(self, session: AsyncSession, email: EmailContext) -> None:
        stmt = insert(Email).values(**email.model_dump())
        await session.execute(stmt)

    async def get(self, session: AsyncSession, id: str) -> EmailContext:
        stmt = select(Email).where(Email.id == id)
        rows = await session.execute(stmt)
        result = rows.scalar_one()
        return EmailContext.model_validate(result)

    async def delete(self, session: AsyncSession, id: str) -> None:
        stmt = delete(Email).where(Email.id == id)
        await session.execute(stmt)

    async def update(self, session: AsyncSession, auth: EmailContext) -> None:
        stmt = update(Email).where(Email.id == auth.id).values(**auth.model_dump())
        await session.execute(stmt)


class ReceiptConnector:
    async def add(self, session: AsyncSession, receipt: ReceiptContext) -> None:
        stmt = insert(ReceiptDetail).values(**receipt.model_dump())
        await session.execute(stmt)

    async def get(self, session: AsyncSession, id: str) -> ReceiptContext:
        stmt = select(ReceiptDetail).where(ReceiptDetail.id == id)
        rows = await session.execute(stmt)
        result = rows.scalar_one()
        return ReceiptContext.model_validate(result)

    async def delete(self, session: AsyncSession, id: str) -> None:
        stmt = delete(ReceiptDetail).where(ReceiptDetail.id == id)
        await session.execute(stmt)

    async def update(self, session: AsyncSession, receipt: ReceiptContext) -> None:
        stmt = (
            update(ReceiptDetail)
            .where(ReceiptDetail.id == receipt.id)
            .values(**receipt.model_dump())
        )
        await session.execute(stmt)
