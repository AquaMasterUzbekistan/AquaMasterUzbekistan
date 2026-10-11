"""Genetics model for morph and line-breeding data."""

from __future__ import annotations

from sqlalchemy import BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class GeneticsMorph(Base):
    __tablename__ = "genetics_morphs"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    morph_name: Mapped[str] = mapped_column(String(255), nullable=False)
    morph_type: Mapped[str | None] = mapped_column(String(100), nullable=True)  # OB, MC, Albino, Longfin...
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    inheritance_pattern: Mapped[str | None] = mapped_column(Text, nullable=True)
    reliability_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    species: Mapped["Species"] = relationship(lazy="selectin")


from app.models.species import Species  # noqa: E402, F401
