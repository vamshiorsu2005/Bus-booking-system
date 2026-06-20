import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Coupon(BaseModel):
    __tablename__ = "coupon"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    discount_type: Mapped[str] = mapped_column(String(20), default="Percentage", nullable=False)  # "Percentage", "Fixed"
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    min_booking_value: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    max_discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)  # Max cap for percentage
    active_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    max_uses: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Offer(BaseModel):
    __tablename__ = "offer"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    banner_url: Mapped[str] = mapped_column(String(255), nullable=True)
    discount_details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    active_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
