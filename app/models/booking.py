import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Booking(BaseModel):
    __tablename__ = "booking"

    pnr: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trip.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="Pending", nullable=False
    )  # "Pending", "Confirmed", "Cancelled", "PartiallyCancelled"
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    coupon_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coupon.id", ondelete="SET NULL"), nullable=True
    )
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    final_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    trip: Mapped["Trip"] = relationship("Trip", back_populates="bookings")
    coupon: Mapped[Optional["Coupon"]] = relationship("Coupon")
    booking_seats: Mapped[List["BookingSeat"]] = relationship(
        "BookingSeat", back_populates="booking", cascade="all, delete-orphan"
    )
    seat_inventories: Mapped[List["SeatInventory"]] = relationship(
        "SeatInventory", back_populates="booking"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="booking", cascade="all, delete-orphan"
    )


class BookingSeat(BaseModel):
    __tablename__ = "booking_seat"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("booking.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="Active", nullable=False
    )  # "Active", "Cancelled"
    refund_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)

    # Relationships
    booking: Mapped[Booking] = relationship(Booking, back_populates="booking_seats")
    refunds: Mapped[List["Refund"]] = relationship("Refund", back_populates="booking_seat", cascade="all, delete-orphan")
