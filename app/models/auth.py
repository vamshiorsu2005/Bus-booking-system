import uuid
from datetime import datetime
from typing import List
from sqlalchemy import Column, Table, ForeignKey, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.core.database import Base

# Association table for many-to-many relationship between Roles and Permissions
role_permission_association = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
)


class Role(BaseModel):
    __tablename__ = "role"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    # Relationships
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=role_permission_association, back_populates="roles"
    )
    users: Mapped[List["User"]] = relationship(
        "User", secondary="user_role", back_populates="roles"
    )


class Permission(BaseModel):
    __tablename__ = "permission"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    # Relationships
    roles: Mapped[List[Role]] = relationship(
        Role, secondary=role_permission_association, back_populates="permissions"
    )


class RefreshToken(BaseModel):
    __tablename__ = "refresh_token"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class Session(BaseModel):
    __tablename__ = "session"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
