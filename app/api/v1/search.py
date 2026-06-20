import datetime
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.trip import TripSearchResponse
from app.services.search import search_service

router = APIRouter()


@router.get("", response_model=List[TripSearchResponse], status_code=status.HTTP_200_OK)
async def search_trips(
    source_city_id: uuid.UUID = Query(..., description="UUID of source city"),
    destination_city_id: uuid.UUID = Query(..., description="UUID of destination city"),
    journey_date: datetime.date = Query(..., description="Date of journey (YYYY-MM-DD)"),
    ac_only: Optional[bool] = Query(None, description="Filter for AC buses only"),
    seat_type: Optional[str] = Query(None, description="Filter seat type: Sleeper | Seater | Semi-Sleeper"),
    bus_type_id: Optional[uuid.UUID] = Query(None, description="Filter by specific bus type UUID"),
    price_min: Optional[float] = Query(None, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, description="Maximum price filter"),
    bypass_cache: bool = Query(False, description="Set to true to bypass cache"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search available trips matching source, destination and date.
    Results are cached in Redis to achieve high-performance sub-200ms lookup.
    """
    trips = await search_service.search_trips(
        db,
        source_city_id=source_city_id,
        destination_city_id=destination_city_id,
        journey_date=journey_date,
        ac_only=ac_only,
        seat_type=seat_type,
        bus_type_id=bus_type_id,
        price_min=price_min,
        price_max=price_max,
        bypass_cache=bypass_cache
    )
    return trips
