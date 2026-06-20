from typing import Any, List, Optional
import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.trip import Schedule, Trip
from app.models.route import Route
from app.models.bus import Bus
from app.models.seat import SeatInventory


class ScheduleRepository(BaseRepository[Schedule]):
    def __init__(self):
        super().__init__(Schedule)

    async def get_by_bus(self, db: AsyncSession, bus_id: Any) -> List[Schedule]:
        query = select(self.model).where(self.model.bus_id == bus_id)
        result = await db.execute(query)
        return list(result.scalars().all())


class TripRepository(BaseRepository[Trip]):
    def __init__(self):
        super().__init__(Trip)

    async def get_with_details(self, db: AsyncSession, id: Any) -> Optional[Trip]:
        query = select(self.model).where(self.model.id == id).options(
            joinedload(self.model.schedule).joinedload(Schedule.bus).joinedload(Bus.bus_type),
            joinedload(self.model.schedule).joinedload(Schedule.route).options(
                joinedload(Route.source_city),
                joinedload(Route.destination_city)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search_trips(
        self,
        db: AsyncSession,
        source_city_id: Any,
        destination_city_id: Any,
        journey_date: datetime.date,
        ac_only: Optional[bool] = None,
        seat_type: Optional[str] = None,
        bus_type_id: Optional[Any] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None
    ) -> List[Trip]:
        """
        Search available trips matching source, destination, and date,
        with optional filters (AC, seat type, price range).
        """
        # Subquery to filter routes between source and destination
        route_query = select(Route.id).where(
            Route.source_city_id == source_city_id,
            Route.destination_city_id == destination_city_id
        )
        route_ids = (await db.execute(route_query)).scalars().all()
        if not route_ids:
            return []

        # Build main trip query
        query = select(self.model).join(self.model.schedule).join(Schedule.bus).join(Bus.bus_type).where(
            self.model.journey_date == journey_date,
            self.model.status != "Cancelled",
            Schedule.route_id.in_(route_ids)
        ).options(
            joinedload(self.model.schedule).joinedload(Schedule.bus).joinedload(Bus.bus_type),
            joinedload(self.model.schedule).joinedload(Schedule.route).options(
                joinedload(Route.source_city),
                joinedload(Route.destination_city)
            ),
            selectinload(self.model.seat_inventories)
        )

        # Filters
        if ac_only is not None:
            from app.models.bus import BusType
            query = query.where(BusType.is_ac == ac_only)
        if seat_type:
            from app.models.bus import BusType
            query = query.where(BusType.seat_type == seat_type)
        if bus_type_id:
            query = query.where(Bus.bus_type_id == bus_type_id)

        result = await db.execute(query)
        trips = list(result.scalars().all())

        # Apply price filters in Python or database. We can do it in database using:
        # Schedule.base_price * Trip.price_modifier
        filtered_trips = []
        for trip in trips:
            final_price = float(trip.schedule.base_price) * float(trip.price_modifier)
            if price_min is not None and final_price < price_min:
                continue
            if price_max is not None and final_price > price_max:
                continue
            filtered_trips.append(trip)

        return filtered_trips


trip_repository = TripRepository()
schedule_repository = ScheduleRepository()
