"""Species model — the central entity of the atlas."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Text, Float, Integer, Boolean,
    DateTime, ForeignKey, Enum as SAEnum, func, Table, Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


# ── Association tables ──────────────────────────────────────────────

species_localities = Table(
    "species_localities",
    Base.metadata,
    Column("species_id", BigInteger, ForeignKey("species.id", ondelete="CASCADE"), primary_key=True),
    Column("locality_id", BigInteger, ForeignKey("localities.id", ondelete="CASCADE"), primary_key=True),
)

species_categories = Table(
    "species_categories",
    Base.metadata,
    Column("species_id", BigInteger, ForeignKey("species.id", ondelete="CASCADE"), primary_key=True),
    Column("subcategory_id", BigInteger, ForeignKey("subcategories.id", ondelete="CASCADE"), primary_key=True),
)


# ── Enums ───────────────────────────────────────────────────────────

class ReliabilityLevel(str, enum.Enum):
    SCIENTIFIC = "scientific"         # 🟢 Ilmiy tasdiqlangan
    HOBBYIST = "hobbyist"            # 🟡 Hobbyist kuzatuvi
    DISPUTED = "disputed"            # 🟠 Bahsli / Noaniq
    UNVERIFIED = "unverified"        # 🔴 Ishonchsiz / Tasdiqlanmagan


class AggressionLevel(str, enum.Enum):
    PEACEFUL = "peaceful"
    SEMI_AGGRESSIVE = "semi_aggressive"
    AGGRESSIVE = "aggressive"
    HIGHLY_AGGRESSIVE = "highly_aggressive"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class BreedingType(str, enum.Enum):
    MOUTHBROODER = "mouthbrooder"
    SUBSTRATE_SPAWNER = "substrate_spawner"
    CAVE_SPAWNER = "cave_spawner"
    SHELL_SPAWNER = "shell_spawner"
    BUBBLE_NEST = "bubble_nest"
    EGG_SCATTERER = "egg_scatterer"
    LIVEBEARER = "livebearer"
    OTHER = "other"


class WaterType(str, enum.Enum):
    FRESHWATER = "freshwater"
    BRACKISH = "brackish"
    MARINE = "marine"


class OriginType(str, enum.Enum):
    WILD = "wild"
    TANK_BRED = "tank_bred"
    SELECTIVE = "selective"
    HYBRID = "hybrid"


# ── Main Species model ──────────────────────────────────────────────

class Species(Base):
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)

    # Core identification
    scientific_name: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    genus_id: Mapped[int] = mapped_column(ForeignKey("genera.id", ondelete="CASCADE"), index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    year_described: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subspecies: Mapped[str | None] = mapped_column(String(255), nullable=True)
    taxonomic_status: Mapped[str | None] = mapped_column(String(100), default="valid", nullable=True)
    conservation_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    depth_range: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Classification
    origin_type: Mapped[OriginType] = mapped_column(
        SAEnum(OriginType), default=OriginType.WILD, nullable=False
    )
    water_type: Mapped[WaterType] = mapped_column(
        SAEnum(WaterType), default=WaterType.FRESHWATER
    )

    # Physical
    max_size_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_shape: Mapped[str | None] = mapped_column(String(255), nullable=True)
    coloration: Mapped[str | None] = mapped_column(Text, nullable=True)
    sexual_dimorphism: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Water parameters
    temp_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    gh_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    gh_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    kh_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    kh_max: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Aquarium
    min_tank_liters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommended_tank_liters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    group_size_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    group_size_recommended: Mapped[str | None] = mapped_column(String(100), nullable=True)
    aggression: Mapped[AggressionLevel | None] = mapped_column(SAEnum(AggressionLevel), nullable=True)
    difficulty: Mapped[DifficultyLevel | None] = mapped_column(SAEnum(DifficultyLevel), nullable=True)

    # Diet
    diet_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    diet_plant: Mapped[str | None] = mapped_column(Text, nullable=True)
    diet_protein: Mapped[str | None] = mapped_column(Text, nullable=True)
    dietary_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Behavior & Compatibility
    temperament: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conspecific_aggression: Mapped[str | None] = mapped_column(Text, nullable=True)
    interspecific_aggression: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Husbandry details
    tank_setup_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    filtration_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    water_changes_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Taxonomy & Evidence Notes
    taxonomic_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_quality_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_verified_date: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Breeding
    breeding_type: Mapped[BreedingType | None] = mapped_column(SAEnum(BreedingType), nullable=True)
    breeding_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fry_care: Mapped[str | None] = mapped_column(Text, nullable=True)
    male_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    female_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Genetics
    genetics_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    color_morphs: Mapped[str | None] = mapped_column(Text, nullable=True)
    wild_form: Mapped[str | None] = mapped_column(Text, nullable=True)
    f_generation: Mapped[str | None] = mapped_column(String(20), nullable=True)  # F0, F1, F2...

    # Habitat
    natural_habitat: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Important note
    important_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reliability
    reliability: Mapped[ReliabilityLevel] = mapped_column(
        SAEnum(ReliabilityLevel), default=ReliabilityLevel.HOBBYIST
    )

    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    search_count: Mapped[int] = mapped_column(Integer, default=0)
    compare_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    genus: Mapped["Genus"] = relationship(back_populates="species_list", lazy="selectin")
    common_names: Mapped[list["CommonName"]] = relationship(
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    synonyms: Mapped[list["Synonym"]] = relationship(
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    trade_names: Mapped[list["TradeName"]] = relationship(
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    images: Mapped[list["SpeciesImage"]] = relationship(
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    sources: Mapped[list["SpeciesSource"]] = relationship(
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    claims: Mapped[list["ScientificClaim"]] = relationship(
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    verification_history: Mapped[list["VerificationHistory"]] = relationship(
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    compatible_with: Mapped[list["Compatibility"]] = relationship(
        foreign_keys="Compatibility.species_id",
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    similar_species: Mapped[list["SimilarSpecies"]] = relationship(
        foreign_keys="SimilarSpecies.species_id",
        back_populates="species", lazy="selectin", cascade="all, delete-orphan"
    )
    localities: Mapped[list["Locality"]] = relationship(
        secondary=species_localities, lazy="selectin"
    )
    subcategories: Mapped[list["Subcategory"]] = relationship(
        secondary=species_categories, lazy="selectin"
    )
    l_numbers: Mapped[list["LNumberDesignation"]] = relationship(
        secondary="lnumber_species",
        back_populates="species_list",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Species {self.scientific_name}>"


class CommonName(Base):
    """Common names in multiple languages."""
    __tablename__ = "common_names"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="uz")  # uz, en, ru

    species: Mapped["Species"] = relationship(back_populates="common_names")


class Synonym(Base):
    """Historical or alternative scientific names."""
    __tablename__ = "synonyms"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    species: Mapped["Species"] = relationship(back_populates="synonyms")


class TradeName(Base):
    """Commercial / aquarium trade names."""
    __tablename__ = "trade_names"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    species: Mapped["Species"] = relationship(back_populates="trade_names")


# Forward references
from app.models.taxonomy import Genus, Subcategory  # noqa: E402, F401
from app.models.locality import Locality  # noqa: E402, F401
from app.models.image import SpeciesImage  # noqa: E402, F401
from app.models.source import SpeciesSource, ScientificClaim, VerificationHistory  # noqa: E402, F401
from app.models.compatibility import Compatibility, SimilarSpecies  # noqa: E402, F401
from app.models.lnumber import LNumberDesignation  # noqa: E402, F401
