import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class StateBase(BaseModel):
    name: str = Field(..., example="Karnataka")
    code: str = Field(..., example="KA")


class StateCreate(StateBase):
    pass


class StateOut(StateBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class CityBase(BaseModel):
    name: str = Field(..., example="Bengaluru")
    code: str = Field(..., example="BLR")


class CityCreate(CityBase):
    state_id: uuid.UUID


class CityOut(CityBase):
    id: uuid.UUID
    state_id: uuid.UUID

    class Config:
        from_attributes = True


class StopBase(BaseModel):
    name: str = Field(..., example="Majestic Bus Stand")
    latitude: Decimal = Field(..., max_digits=9, decimal_places=6)
    longitude: Decimal = Field(..., max_digits=9, decimal_places=6)
    address: Optional[str] = Field(None, example="Kempegowda Bus Station, Majestic")


class StopCreate(StopBase):
    city_id: uuid.UUID


class StopOut(StopBase):
    id: uuid.UUID
    city_id: uuid.UUID

    class Config:
        from_attributes = True


class RouteStopCreate(BaseModel):
    stop_id: uuid.UUID
    sequence: int = Field(..., ge=1)
    distance_from_source: Decimal = Field(..., max_digits=6, decimal_places=2)
    time_from_source_mins: int = Field(..., ge=0)


class RouteStopOut(BaseModel):
    id: uuid.UUID
    route_id: uuid.UUID
    stop: StopOut
    sequence: int
    distance_from_source: Decimal
    time_from_source_mins: int

    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    source_city_id: uuid.UUID
    destination_city_id: uuid.UUID
    distance_km: Decimal = Field(..., max_digits=6, decimal_places=2)
    duration_minutes: int = Field(..., ge=1)
    stops: List[RouteStopCreate] = Field(default_factory=list)


class RouteOut(BaseModel):
    id: uuid.UUID
    source_city: CityOut
    destination_city: CityOut
    distance_km: Decimal
    duration_minutes: int
    route_stops: List[RouteStopOut] = []

    class Config:
        from_attributes = True
