import uuid
import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from app.schemas.bus import BusOut
from app.schemas.route import RouteOut, CityOut


class ScheduleCreate(BaseModel):
    bus_id: uuid.UUID
    route_id: uuid.UUID
    departure_time: datetime.time
    arrival_time: datetime.time
    days_of_week: int = Field(default=127, description="Bitmask for active days. e.g., 127 = everyday")
    base_price: Decimal = Field(..., max_digits=10, decimal_places=2)


class ScheduleOut(BaseModel):
    id: uuid.UUID
    bus_id: uuid.UUID
    route_id: uuid.UUID
    departure_time: datetime.time
    arrival_time: datetime.time
    days_of_week: int
    base_price: Decimal
    is_active: bool

    class Config:
        from_attributes = True


class TripCreate(BaseModel):
    schedule_id: uuid.UUID
    journey_date: datetime.date
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    price_modifier: Decimal = Field(default=1.00, max_digits=4, decimal_places=2)
    status: str = Field(default="Scheduled")


class TripOut(BaseModel):
    id: uuid.UUID
    schedule_id: uuid.UUID
    journey_date: datetime.date
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    price_modifier: Decimal
    status: str

    class Config:
        from_attributes = True


class TripSearchResponse(BaseModel):
    trip_id: uuid.UUID
    journey_date: datetime.date
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    base_price: Decimal
    final_price: Decimal
    status: str
    bus: BusOut
    route: RouteOut
    available_seats: int

    class Config:
        from_attributes = True
