import uuid
from typing import List
from sqlalchemy import ForeignKey, String, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class State(BaseModel):
    __tablename__ = "state"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False, index=True)

    # Relationships
    cities: Mapped[List["City"]] = relationship("City", back_populates="state", cascade="all, delete-orphan")


class City(BaseModel):
    __tablename__ = "city"

    state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("state.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)

    # Relationships
    state: Mapped[State] = relationship(State, back_populates="cities")
    stops: Mapped[List["Stop"]] = relationship("Stop", back_populates="city", cascade="all, delete-orphan")


class Stop(BaseModel):
    __tablename__ = "stop"

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    city: Mapped[City] = relationship(City, back_populates="stops")
    route_stops: Mapped[List["RouteStop"]] = relationship("RouteStop", back_populates="stop", cascade="all, delete-orphan")


class Route(BaseModel):
    __tablename__ = "route"

    source_city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    destination_city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    distance_km: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    source_city: Mapped[City] = relationship(City, foreign_keys=[source_city_id])
    destination_city: Mapped[City] = relationship(City, foreign_keys=[destination_city_id])
    route_stops: Mapped[List["RouteStop"]] = relationship("RouteStop", back_populates="route", cascade="all, delete-orphan")
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="route", cascade="all, delete-orphan")


class RouteStop(BaseModel):
    __tablename__ = "route_stop"

    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stop.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_from_source: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    time_from_source_mins: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    route: Mapped[Route] = relationship(Route, back_populates="route_stops")
    stop: Mapped[Stop] = relationship(Stop, back_populates="route_stops")
