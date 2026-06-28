from abc import ABC, abstractmethod

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import BaseConfig
from src.db.orm import Config


class AbstractConnector(ABC):
    @abstractmethod
    async def add(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        raise NotImplementedError


class ConfigConnector:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, config: BaseConfig):
        stmt = insert(Config).values(config.model_dump())
        await self.session.execute(stmt)
        await self.session.flush()

    async def get(self, email: str) -> Config | None:
        stmt = select(Config).where(Config.email == email)
        result = await self.session.execute(stmt)
        config = result.first()
        if config is None:
            return None
        return config[0]

    async def delete(self, email: str): ...


class AuthenticationConnector(AbstractConnector):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self) -> None:
        pass


class UserConnector(AbstractConnector):
    pass
