"""Compatibility and similar species models."""

from __future__ import annotations

import enum

from sqlalchemy import BigInteger, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class CompatibilityLevel(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    CAUTION = "caution"
    INCOMPATIBLE = "incompatible"


class Compatibility(Base):
    __tablename__ = "compatibility"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    target_species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    level: Mapped[CompatibilityLevel] = mapped_column(SAEnum(CompatibilityLevel), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    species: Mapped["Species"] = relationship(
        foreign_keys=[species_id], back_populates="compatible_with"
    )
    target_species: Mapped["Species"] = relationship(
        foreign_keys=[target_species_id], lazy="selectin"
    )


class SimilarSpecies(Base):
    __tablename__ = "similar_species"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    similar_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_difference: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_difference: Mapped[str | None] = mapped_column(Text, nullable=True)
    mouth_difference: Mapped[str | None] = mapped_column(Text, nullable=True)
    fin_difference: Mapped[str | None] = mapped_column(Text, nullable=True)
    color_difference: Mapped[str | None] = mapped_column(Text, nullable=True)

    species: Mapped["Species"] = relationship(
        foreign_keys=[species_id], back_populates="similar_species"
    )
    similar: Mapped["Species"] = relationship(
        foreign_keys=[similar_id], lazy="selectin"
    )


from app.models.species import Species  # noqa: E402, F401
