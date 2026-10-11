from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.context import AuthContext, EmailContext, ReceiptContext
from src.db.orm import Authentication, Email, ReceiptDetail


class AuthenticationConnector:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def add(self, auth: AuthContext) -> None:
        async with self._session_factory.begin() as session:
            stmt = insert(Authentication).values(**auth.model_dump())
            await session.execute(stmt)
            await session.commit()

    async def get(self, email: str) -> AuthContext:
        async with self._session_factory.begin() as session:
            stmt = select(Authentication).where(Authentication.email == email)
            rows = await session.execute(stmt)
            result = rows.scalar_one()
            return AuthContext.model_validate(result)

    async def delete(self, email: str) -> None:
        async with self._session_factory.begin() as session:
            stmt = delete(Authentication).where(Authentication.email == email)
            await session.execute(stmt)
            await session.commit()

    async def update(self, auth: AuthContext) -> None:
        async with self._session_factory.begin() as session:
            stmt = (
                update(Authentication)
                .where(Authentication.email == auth.email)
                .values(**auth.model_dump())
            )
            await session.execute(stmt)
            await session.commit()


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
