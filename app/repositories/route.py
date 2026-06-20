from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.route import Route, State, City, Stop, RouteStop


class RouteRepository(BaseRepository[Route]):
    def __init__(self):
        super().__init__(Route)

    async def get_with_details(self, db: AsyncSession, id: Any) -> Optional[Route]:
        query = select(self.model).where(self.model.id == id).options(
            joinedload(self.model.source_city),
            joinedload(self.model.destination_city),
            selectinload(self.model.route_stops).joinedload(RouteStop.stop)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def find_route(self, db: AsyncSession, source_city_id: Any, destination_city_id: Any) -> Optional[Route]:
        query = select(self.model).where(
            self.model.source_city_id == source_city_id,
            self.model.destination_city_id == destination_city_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


class StateRepository(BaseRepository[State]):
    def __init__(self):
        super().__init__(State)


class CityRepository(BaseRepository[City]):
    def __init__(self):
        super().__init__(City)

    async def get_by_state(self, db: AsyncSession, state_id: Any) -> List[City]:
        query = select(self.model).where(self.model.state_id == state_id)
        result = await db.execute(query)
        return list(result.scalars().all())


class StopRepository(BaseRepository[Stop]):
    def __init__(self):
        super().__init__(Stop)

    async def get_by_city(self, db: AsyncSession, city_id: Any) -> List[Stop]:
        query = select(self.model).where(self.model.city_id == city_id)
        result = await db.execute(query)
        return list(result.scalars().all())


route_repository = RouteRepository()
state_repository = StateRepository()
city_repository = CityRepository()
stop_repository = StopRepository()
