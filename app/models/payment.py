import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Payment(BaseModel):
    __tablename__ = "payment"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("booking.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    transaction_reference: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    gateway: Mapped[str] = mapped_column(String(50), default="Mock", nullable=False)  # "Mock", "Stripe", "Razorpay"
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="Pending", nullable=False
    )  # "Pending", "Success", "Failed", "Refunded"
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="payments")
    refunds: Mapped[List["Refund"]] = relationship("Refund", back_populates="payment", cascade="all, delete-orphan")


class Refund(BaseModel):
    __tablename__ = "refund"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payment.id", ondelete="CASCADE"), nullable=False, index=True
    )
    booking_seat_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("booking_seat.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="Pending", nullable=False
    )  # "Pending", "Success", "Failed"
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    payment: Mapped[Payment] = relationship(Payment, back_populates="refunds")
    booking_seat: Mapped[Optional["BookingSeat"]] = relationship("BookingSeat", back_populates="refunds")
