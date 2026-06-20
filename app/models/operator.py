import uuid
from typing import List
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Operator(BaseModel):
    __tablename__ = "operator"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gst_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="operator")
    buses: Mapped[List["Bus"]] = relationship("Bus", back_populates="operator", cascade="all, delete-orphan")
