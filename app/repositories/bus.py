from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.bus import Bus, BusType, SeatLayout


class BusRepository(BaseRepository[Bus]):
    def __init__(self):
        super().__init__(Bus)

    async def get_by_registration(self, db: AsyncSession, registration_number: str) -> Optional[Bus]:
        query = select(self.model).where(self.model.registration_number == registration_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_operator(self, db: AsyncSession, operator_id: Any) -> List[Bus]:
        query = select(self.model).where(self.model.operator_id == operator_id).options(
            selectinload(self.model.bus_type)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_with_details(self, db: AsyncSession, id: Any) -> Optional[Bus]:
        query = select(self.model).where(self.model.id == id).options(
            selectinload(self.model.bus_type)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


class BusTypeRepository(BaseRepository[BusType]):
    def __init__(self):
        super().__init__(BusType)

    async def get_with_layout(self, db: AsyncSession, id: Any) -> Optional[BusType]:
        query = select(self.model).where(self.model.id == id).options(
            selectinload(self.model.seat_layouts)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


bus_repository = BusRepository()
bus_type_repository = BusTypeRepository()
