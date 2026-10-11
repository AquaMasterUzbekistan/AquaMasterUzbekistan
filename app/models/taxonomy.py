"""Taxonomy models: Family, Genus, Category, Subcategory."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class Category(Base):
    """Top-level categories: African Cichlids, American Cichlids, Discus, etc."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )

    parent: Mapped["Category | None"] = relationship(
        "Category", remote_side="Category.id", lazy="selectin"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent", lazy="selectin"
    )
    subcategories: Mapped[list["Subcategory"]] = relationship(
        back_populates="category", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Subcategory(Base):
    """Sub-groupings: Mbuna, Haps, Peacock, Shell Dwellers, etc."""
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    sort_order: Mapped[int] = mapped_column(default=0)

    category: Mapped["Category"] = relationship(back_populates="subcategories", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Subcategory {self.name}>"


class Family(Base):
    """Taxonomic family, e.g. Cichlidae."""
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    scientific_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    common_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    order_name: Mapped[str | None] = mapped_column(String(100), default="Cichliformes", nullable=True)
    class_name: Mapped[str | None] = mapped_column(String(100), default="Actinopterygii", nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Detailed encyclopedia fields (Section 7)
    general_biology: Mapped[str | None] = mapped_column(Text, nullable=True)
    distribution_overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    feeding_ecology: Mapped[str | None] = mapped_column(Text, nullable=True)
    reproduction_overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    aquarium_care_overview: Mapped[str | None] = mapped_column(Text, nullable=True)

    genera: Mapped[list["Genus"]] = relationship(back_populates="family", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Family {self.scientific_name}>"


class Genus(Base):
    """Taxonomic genus, e.g. Pseudotropheus."""
    __tablename__ = "genera"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    scientific_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    year_described: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subfamily: Mapped[str | None] = mapped_column(String(100), nullable=True)
    common_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )

    # Detailed genus fields (Section 7)
    type_species: Mapped[str | None] = mapped_column(String(255), nullable=True)
    diagnostic_traits: Mapped[str | None] = mapped_column(Text, nullable=True)
    distribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    taxonomic_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    family: Mapped["Family"] = relationship(back_populates="genera", lazy="selectin")
    species_list: Mapped[list["Species"]] = relationship(back_populates="genus", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Genus {self.scientific_name}>"


# Forward reference
from app.models.species import Species  # noqa: E402, F401
