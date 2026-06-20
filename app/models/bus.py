import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class BusType(BaseModel):
    __tablename__ = "bus_type"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_ac: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    seat_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "Sleeper" or "Seater" or "Semi-Sleeper"
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    buses: Mapped[List["Bus"]] = relationship("Bus", back_populates="bus_type")
    seat_layouts: Mapped[List["SeatLayout"]] = relationship("SeatLayout", back_populates="bus_type", cascade="all, delete-orphan")


class SeatLayout(BaseModel):
    __tablename__ = "seat_layout"

    bus_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bus_type.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    row: Mapped[int] = mapped_column(Integer, nullable=False)
    col: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_tier: Mapped[str] = mapped_column(String(10), default="Lower", nullable=False)  # "Lower" or "Upper"
    is_sleeper: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    bus_type: Mapped[BusType] = relationship(BusType, back_populates="seat_layouts")


class Bus(BaseModel):
    __tablename__ = "bus"

    operator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operator.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bus_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bus_type.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    registration_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    amenities: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # e.g. {"wifi": true, "water": true}
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    operator: Mapped["Operator"] = relationship("Operator", back_populates="buses")
    bus_type: Mapped[BusType] = relationship(BusType, back_populates="buses")
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="bus", cascade="all, delete-orphan")
