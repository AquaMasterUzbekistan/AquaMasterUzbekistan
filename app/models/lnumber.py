"""L-number and LDA-number catfish designations models (Section 4).

Dedicated catalog for Loricariidae, Ancistrus, Hypancistrus, Panaque, Baryancistrus,
and other armored catfishes under DATZ / Transfish aquarium designations.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    BigInteger, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, Table, Column, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


# ── Association table between L-number designations and formally described Species ──
lnumber_species = Table(
    "lnumber_species",
    Base.metadata,
    Column("lnumber_id", BigInteger, ForeignKey("l_number_designations.id", ondelete="CASCADE"), primary_key=True),
    Column("species_id", BigInteger, ForeignKey("species.id", ondelete="CASCADE"), primary_key=True),
    Column("is_primary", Boolean, default=True),
    Column("notes", String(255), nullable=True),
)


class LNumberDesignation(Base):
    """Dedicated entity for L-number and LDA-number plecos and armored catfishes."""
    __tablename__ = "l_number_designations"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    designation: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    number_type: Mapped[str] = mapped_column(String(10), default="L", index=True)  # "L" or "LDA"
    code_number: Mapped[int] = mapped_column(Integer, index=True)

    # Scientific identity & status
    scientific_name_current: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    identification_status: Mapped[str] = mapped_column(
        String(50), default="verified", index=True
    )  # "verified", "provisional", "undescribed"
    genus_name: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    family_name: Mapped[str] = mapped_column(String(100), default="Loricariidae", index=True)
    subfamily_name: Mapped[str | None] = mapped_column(String(100), default="Ancistrinae", nullable=True)

    # Common & Trade names
    common_name_uz: Mapped[str | None] = mapped_column(String(255), nullable=True)
    common_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    common_name_ru: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trade_names: Mapped[str | None] = mapped_column(String(500), nullable=True)
    alternative_numbers: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Distribution & Ecology
    river_basin: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    locality_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Physical & Care Parameters
    max_size_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    dietary_category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    aquarium_care: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Taxonomic metadata
    source_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_verified_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_ancistrus: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Many-to-many relationship with Species
    species_list: Mapped[list["Species"]] = relationship(
        secondary=lnumber_species,
        back_populates="l_numbers",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<LNumber {self.designation}: {self.scientific_name_current or 'Undescribed'}>"


from app.models.species import Species  # noqa: E402, F401
