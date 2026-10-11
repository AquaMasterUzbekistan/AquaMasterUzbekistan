"""Breeding journal model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Text, Integer, DateTime,
    ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class BreedingRecord(Base):
    __tablename__ = "breeding_records"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    species_id: Mapped[int | None] = mapped_column(
        ForeignKey("species.id", ondelete="SET NULL"), nullable=True, index=True
    )
    male_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    female_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pair_group: Mapped[str | None] = mapped_column(String(100), nullable=True)
    spawning_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    egg_holding_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estimated_hatch_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fry_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    survival_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="breeding_records")
    species: Mapped["Species | None"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<BreedingRecord {self.id}>"


from app.models.user import User  # noqa: E402, F401
from app.models.species import Species  # noqa: E402, F401
