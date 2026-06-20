import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class SeatInventory(BaseModel):
    __tablename__ = "seat_inventory"

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trip.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Available", nullable=False)  # "Available", "Locked", "Booked"
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    booking_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("booking.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="seat_inventories")
    locked_by_user: Mapped[Optional["User"]] = relationship("User")
    booking: Mapped[Optional["Booking"]] = relationship("Booking", back_populates="seat_inventories")
