import uuid
import datetime
from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bus import Bus, BusType, SeatLayout
from app.models.route import Route, RouteStop
from app.models.trip import Schedule, Trip
from app.models.seat import SeatInventory
from app.repositories.bus import bus_repository, bus_type_repository
from app.repositories.route import route_repository
from app.repositories.trip import schedule_repository, trip_repository
from app.schemas.bus import BusCreate, BusTypeCreate, SeatLayoutCreate
from app.schemas.route import RouteCreate
from app.schemas.trip import ScheduleCreate, TripCreate
from app.core.exceptions import DomainException


class OperatorService:
    async def create_bus_type(
        self, db: AsyncSession, bus_type_in: BusTypeCreate, layouts: List[SeatLayoutCreate]
    ) -> BusType:
        """Create a BusType and template its SeatLayout."""
        # Save BusType
        bus_type_data = bus_type_in.model_dump()
        bus_type = BusType(**bus_type_data)
        db.add(bus_type)
        await db.flush()

        # Save SeatLayouts
        for layout_in in layouts:
            layout = SeatLayout(
                bus_type_id=bus_type.id,
                **layout_in.model_dump()
            )
            db.add(layout)
        
        await db.flush()
        return bus_type

    async def create_bus(self, db: AsyncSession, operator_id: uuid.UUID, bus_in: BusCreate) -> Bus:
        """Register a bus profile for the operator."""
        # Verify BusType exists
        bus_type = await bus_type_repository.get(db, bus_in.bus_type_id)
        if not bus_type:
            raise DomainException("Bus type not found", code="BUS_TYPE_NOT_FOUND")

        # Verify registration number is unique
        existing = await bus_repository.get_by_registration(db, bus_in.registration_number)
        if existing:
            raise DomainException(
                f"Bus with registration {bus_in.registration_number} already exists",
                code="DUPLICATE_REGISTRATION"
            )

        bus_data = bus_in.model_dump()
        bus_data["operator_id"] = operator_id
        bus = Bus(**bus_data)
        db.add(bus)
        await db.flush()
        return bus

    async def create_route(self, db: AsyncSession, route_in: RouteCreate) -> Route:
        """Create a route with sequential stops."""
        # Check if route already exists directly
        existing = await route_repository.find_route(db, route_in.source_city_id, route_in.destination_city_id)
        if existing:
            raise DomainException("Route already exists", code="ROUTE_ALREADY_EXISTS")

        route = Route(
            source_city_id=route_in.source_city_id,
            destination_city_id=route_in.destination_city_id,
            distance_km=route_in.distance_km,
            duration_minutes=route_in.duration_minutes
        )
        db.add(route)
        await db.flush()

        # Add Stops
        for stop_in in route_in.stops:
            route_stop = RouteStop(
                route_id=route.id,
                stop_id=stop_in.stop_id,
                sequence=stop_in.sequence,
                distance_from_source=stop_in.distance_from_source,
                time_from_source_mins=stop_in.time_from_source_mins
            )
            db.add(route_stop)

        await db.flush()
        return route

    async def create_schedule(self, db: AsyncSession, schedule_in: ScheduleCreate) -> Schedule:
        """Define a schedule for a bus on a route."""
        # Verify bus and route exist
        bus = await bus_repository.get(db, schedule_in.bus_id)
        if not bus:
            raise DomainException("Bus not found", code="BUS_NOT_FOUND")
        
        route = await route_repository.get(db, schedule_in.route_id)
        if not route:
            raise DomainException("Route not found", code="ROUTE_NOT_FOUND")

        schedule = Schedule(**schedule_in.model_dump())
        db.add(schedule)
        await db.flush()
        return schedule

    async def generate_trip(self, db: AsyncSession, trip_in: TripCreate) -> Trip:
        """Generate a concrete trip from a schedule for a specific date and initialize its seats."""
        schedule = await schedule_repository.get(db, trip_in.schedule_id)
        if not schedule:
            raise DomainException("Schedule not found", code="SCHEDULE_NOT_FOUND")

        # Load the bus layout template
        query = select(SeatLayout).where(SeatLayout.bus_type_id == select(Bus.bus_type_id).where(Bus.id == schedule.bus_id).scalar_subquery())
        layouts_result = await db.execute(query)
        layouts = list(layouts_result.scalars().all())

        if not layouts:
            raise DomainException("No seat layouts configured for this bus type", code="NO_SEAT_LAYOUT")

        # Create concrete Trip
        trip = Trip(
            schedule_id=trip_in.schedule_id,
            journey_date=trip_in.journey_date,
            departure_time=trip_in.departure_time,
            arrival_time=trip_in.arrival_time,
            price_modifier=trip_in.price_modifier,
            status=trip_in.status
        )
        db.add(trip)
        await db.flush()

        # Initialize Seat Inventory from the templates
        for layout in layouts:
            seat_inv = SeatInventory(
                trip_id=trip.id,
                seat_number=layout.seat_number,
                status="Available"
            )
            db.add(seat_inv)
        
        await db.flush()
        return trip


operator_service = OperatorService()
