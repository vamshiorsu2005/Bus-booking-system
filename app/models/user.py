import uuid
from typing import List, Optional
from sqlalchemy import Column, Table, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.core.database import Base

# Association table for User-Role mapping (supporting multiple roles per user if needed)
user_role_association = Table(
    "user_role",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)


class User(BaseModel):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=user_role_association, back_populates="users"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    operator: Mapped[Optional["Operator"]] = relationship(
        "Operator", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )
