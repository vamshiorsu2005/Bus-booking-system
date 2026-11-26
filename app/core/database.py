from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# For high performance under concurrent bookings, configure optimized pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=50,             # Number of permanent connections
    max_overflow=20,          # Extra connections allowed during peak traffic
    pool_recycle=1800,        # Recycle connections every 30 minutes to prevent timeouts
    pool_pre_ping=True,       # Validate connections before using them
    echo=settings.DEBUG and settings.ENV == "development"
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining database sessions in FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
