import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.config import settings
from app.core.database import get_db, Base
from app.core.redis import redis_service

# Create a clean engine for testing.
# We'll use the same connection, but rollback transactions after each test.
test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session that rolls back after every test."""
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        session = TestingSessionLocal(bind=connection)

        # Yield the session
        yield session

        # Roll back everything after the test completes
        await session.close()
        await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient configured to request our FastAPI app."""
    # Override get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def flush_redis():
    """Automatically flush Redis database before each test to prevent cross-test contamination."""
    await redis_service.client.flushdb()
    yield
