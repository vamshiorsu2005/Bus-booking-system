import uuid
from datetime import date, datetime, time
from typing import List
from sqlalchemy import ForeignKey, Time, DateTime, Date, Numeric, Integer, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Schedule(BaseModel):
    __tablename__ = "schedule"

    bus_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route.id", ondelete="CASCADE"), nullable=False, index=True
    )
    departure_time: Mapped[time] = mapped_column(Time, nullable=False)
    arrival_time: Mapped[time] = mapped_column(Time, nullable=False)
    days_of_week: Mapped[int] = mapped_column(Integer, default=127, nullable=False)  # Bitmask (e.g., 127 = 1111111 binary = all days)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    bus: Mapped["Bus"] = relationship("Bus", back_populates="schedules")
    route: Mapped["Route"] = relationship("Route", back_populates="schedules")
    trips: Mapped[List["Trip"]] = relationship("Trip", back_populates="schedule", cascade="all, delete-orphan")


class Trip(BaseModel):
    __tablename__ = "trip"

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False, index=True
    )
    journey_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price_modifier: Mapped[float] = mapped_column(Numeric(4, 2), default=1.00, nullable=False)  # Dynamic price scaling (e.g., 1.20 = +20%)
    status: Mapped[str] = mapped_column(String(20), default="Scheduled", nullable=False)  # "Scheduled", "Delayed", "Completed", "Cancelled"

    # Relationships
    schedule: Mapped[Schedule] = relationship(Schedule, back_populates="trips")
    seat_inventories: Mapped[List["SeatInventory"]] = relationship("SeatInventory", back_populates="trip", cascade="all, delete-orphan")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")
