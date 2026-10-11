"""Source, citation, scientific claim, and audit history models."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Text, DateTime, ForeignKey, Integer,
    Enum as SAEnum, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class ConfidenceLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)  # journal, database, book
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    claims: Mapped[list["ScientificClaim"]] = relationship(back_populates="source", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Source {self.name}>"


class SpeciesSource(Base):
    __tablename__ = "species_sources"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), index=True
    )
    relevant_section: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        SAEnum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM
    )

    species: Mapped["Species"] = relationship(back_populates="sources")
    source: Mapped["Source"] = relationship(lazy="selectin")


class ScientificClaim(Base):
    """Specific scientific claim tied to a species, source, exact URL, and evidence rating."""
    __tablename__ = "scientific_claims"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    claim_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True
    )
    exact_source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_section: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidence_label: Mapped[str] = mapped_column(String(50), default="scientific")
    verified_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    species: Mapped["Species"] = relationship(back_populates="claims")
    source: Mapped["Source | None"] = relationship(back_populates="claims", lazy="selectin")


class VerificationHistory(Base):
    """Audit log tracking taxonomic and ecological edits."""
    __tablename__ = "verification_history"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(100), default="system")
    source_citation: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    species: Mapped["Species"] = relationship(back_populates="verification_history")


class ImportLog(Base):
    """Record of ingestion pipeline batch runs."""
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    batch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


from app.models.species import Species  # noqa: E402, F401
