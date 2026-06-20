import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class BusTypeBase(BaseModel):
    name: str = Field(..., example="Scania Multi-Axle Sleeper")
    is_ac: bool = Field(default=True)
    seat_type: str = Field(..., example="Sleeper", description="Sleeper | Seater | Semi-Sleeper")
    capacity: int = Field(..., gt=0)


class BusTypeCreate(BusTypeBase):
    pass


class BusTypeOut(BusTypeBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class SeatLayoutBase(BaseModel):
    seat_number: str = Field(..., example="A1")
    row: int = Field(..., ge=0)
    col: int = Field(..., ge=0)
    seat_tier: str = Field(default="Lower", description="Lower | Upper")
    is_sleeper: bool = Field(default=False)


class SeatLayoutCreate(SeatLayoutBase):
    pass


class SeatLayoutOut(SeatLayoutBase):
    id: uuid.UUID
    bus_type_id: uuid.UUID

    class Config:
        from_attributes = True


class BusBase(BaseModel):
    name: str = Field(..., example="VRL Travels - Mercedes Benz")
    registration_number: str = Field(..., example="KA-01-F-1234")
    amenities: Dict[str, bool] = Field(default_factory=dict, description="e.g. {'wifi': true, 'water': true}")
    is_active: bool = Field(default=True)


class BusCreate(BusBase):
    bus_type_id: uuid.UUID


class BusUpdate(BaseModel):
    name: Optional[str] = None
    registration_number: Optional[str] = None
    amenities: Optional[Dict[str, bool]] = None
    is_active: Optional[bool] = None
    bus_type_id: Optional[uuid.UUID] = None


class BusOut(BusBase):
    id: uuid.UUID
    operator_id: uuid.UUID
    bus_type: BusTypeOut

    class Config:
        from_attributes = True
