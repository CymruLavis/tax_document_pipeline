from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DB_URL = "sqlite+pysqlite:///:memorty:"
engine = create_async_engine(DB_URL, echo=True, pool_pre_ping=True)

session_factory = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
