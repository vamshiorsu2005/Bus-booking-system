from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.api.deps import get_db, RoleRequired
from app.models.user import User
from app.models.operator import Operator
from app.schemas.bus import BusCreate, BusOut, BusTypeCreate, BusTypeOut, SeatLayoutCreate
from app.schemas.route import RouteCreate, RouteOut
from app.schemas.trip import ScheduleCreate, ScheduleOut, TripCreate, TripOut
from app.services.operator import operator_service
from app.core.exceptions import DomainException

router = APIRouter()

# Enforce Bus Operator or Admin roles for all fleet routes
operator_guard = RoleRequired(["Bus Operator", "Admin"])


@router.post("/bus-types", response_model=BusTypeOut, status_code=status.HTTP_201_CREATED)
async def create_bus_type(
    bus_type_in: BusTypeCreate,
    layouts: List[SeatLayoutCreate],
    current_user: User = Depends(operator_guard),
    db: AsyncSession = Depends(get_db)
):
    """Create a bus type template and its seat coordinate layouts."""
    try:
        bus_type = await operator_service.create_bus_type(db, bus_type_in, layouts)
        await db.commit()
        return bus_type
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/buses", response_model=BusOut, status_code=status.HTTP_201_CREATED)
async def create_bus(
    bus_in: BusCreate,
    current_user: User = Depends(operator_guard),
    db: AsyncSession = Depends(get_db)
):
    """Register a new bus profile owned by the operator."""
    try:
        # Fetch operator profile for the current user
        query = select(Operator).where(Operator.user_id == current_user.id)
        result = await db.execute(query)
        operator_profile = result.scalar_one_or_none()
        if not operator_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operator profile not found."
            )

        bus = await operator_service.create_bus(db, operator_profile.id, bus_in)
        await db.commit()
        return bus
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/routes", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_in: RouteCreate,
    current_user: User = Depends(operator_guard),
    db: AsyncSession = Depends(get_db)
):
    """Create a geographic route with stops."""
    try:
        route = await operator_service.create_route(db, route_in)
        await db.commit()
        return route
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/schedules", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_in: ScheduleCreate,
    current_user: User = Depends(operator_guard),
    db: AsyncSession = Depends(get_db)
):
    """Define a recurring schedule for a bus on a route."""
    try:
        schedule = await operator_service.create_schedule(db, schedule_in)
        await db.commit()
        return schedule
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/trips", response_model=TripOut, status_code=status.HTTP_201_CREATED)
async def generate_trip(
    trip_in: TripCreate,
    current_user: User = Depends(operator_guard),
    db: AsyncSession = Depends(get_db)
):
    """Instantiate a concrete trip instance and initialize its seat inventories."""
    try:
        trip = await operator_service.generate_trip(db, trip_in)
        await db.commit()
        return trip
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
