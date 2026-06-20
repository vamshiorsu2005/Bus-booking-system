from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email).options(
            selectinload(self.model.roles)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_roles(self, db: AsyncSession, id: Any) -> Optional[User]:
        query = select(self.model).where(self.model.id == id).options(
            selectinload(self.model.roles)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


user_repository = UserRepository()
