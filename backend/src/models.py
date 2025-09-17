from __future__ import annotations
import sqlalchemy

from typing import Optional, List
from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, Table, Column, Index, func

class Building(Base):
    __tablename__ = "buildings"
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(255), unique=True)
    latitude: Mapped[float] = mapped_column(Float, index=False)
    longitude: Mapped[float] = mapped_column(Float, index=False)

    organizations: Mapped[List[Organization]] = relationship(back_populates="building")

    __table_args__ = (
        Index("ix_buildings_lat_lon", "latitude", "longitude"),
    )

org_act_assoc = Table(
    "organization_activities",
    Base.metadata,
    Column("organization_id", ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("activity_id", ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_org_act_activity_id", "activity_id"),
)

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id", ondelete="RESTRICT"), index=True)

    building: Mapped[Building] = relationship(back_populates="organizations")
    phones: Mapped[List[OrganizationPhones]] = relationship(back_populates="organization", passive_deletes=True)
    activities: Mapped[List[Activity]] = relationship(secondary=org_act_assoc, back_populates="organizations", passive_deletes=True)

    __table_args__ = (
        Index("ix_organization_name_lower", func.lower(name)),
    )

class OrganizationPhones(Base):
    __tablename__ = "organization_phones"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(50), unique=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    organization: Mapped[Organization] = relationship(back_populates="phones", passive_deletes=True)


class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("activities.id", ondelete="SET NULL"))
    
    children: Mapped[List["Activity"]] = relationship(
        back_populates="parent",
        lazy="select"
    )
    parent: Mapped[Optional["Activity"]] = relationship(
        back_populates="children",
        remote_side=[id],
        lazy="select"
    )
    organizations: Mapped[List[Organization]] = relationship(secondary=org_act_assoc, back_populates="activities", passive_deletes=True)

