from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


class AppContext:
    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession], engine: AsyncEngine
    ):

        self.session_factory = session_factory
        self.engine = engine
