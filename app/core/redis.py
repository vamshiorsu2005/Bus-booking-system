from typing import AsyncGenerator, Optional
import redis.asyncio as aioredis
from app.core.config import settings

# Initialize a global connection pool for Redis to support thousands of requests per second
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=100,  # Optimal pool size for high-scale concurrent locking and caching
    decode_responses=True
)


class RedisService:
    def __init__(self):
        self.client = aioredis.Redis(connection_pool=redis_pool)

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        return await self.client.set(key, value, ex=expire)

    async def delete(self, key: str) -> int:
        return await self.client.delete(key)

    async def acquire_lock(self, lock_name: str, acquire_timeout: int = 5, lock_timeout: int = 10) -> Optional[str]:
        """
        Acquires a distributed lock using SET NX PX.
        Returns the lock identifier if acquired, None otherwise.
        """
        import uuid
        import asyncio

        identifier = str(uuid.uuid4())
        lock_key = f"lock:{lock_name}"
        end = asyncio.get_event_loop().time() + acquire_timeout

        while asyncio.get_event_loop().time() < end:
            if await self.client.set(lock_key, identifier, nx=True, ex=lock_timeout):
                return identifier
            await asyncio.sleep(0.1)
        return None

    async def release_lock(self, lock_name: str, identifier: str) -> bool:
        """
        Releases a distributed lock safely using a Lua script to ensure atomicity.
        Only releases the lock if it matches the identifier.
        """
        lock_key = f"lock:{lock_name}"
        # Lua script to release the lock if value matches
        lua_release = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        result = await self.client.eval(lua_release, 1, lock_key, identifier)
        return bool(result)


redis_service = RedisService()


async def get_redis() -> AsyncGenerator[RedisService, None]:
    """FastAPI Dependency for Redis service."""
    yield redis_service
