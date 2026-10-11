"""Locality, Lake, Country, Continent models."""

from __future__ import annotations

from sqlalchemy import BigInteger, String, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class Continent(Base):
    __tablename__ = "continents"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)

    countries: Mapped[list["Country"]] = relationship(back_populates="continent", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Continent {self.name}>"


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(String(5), nullable=True)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    continent_id: Mapped[int] = mapped_column(
        ForeignKey("continents.id", ondelete="CASCADE"), index=True
    )

    continent: Mapped["Continent"] = relationship(back_populates="countries")
    lakes: Mapped[list["Lake"]] = relationship(back_populates="country", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Country {self.name}>"


class Lake(Base):
    __tablename__ = "lakes"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"), nullable=True, index=True
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    country: Mapped["Country | None"] = relationship(back_populates="lakes", lazy="selectin")
    localities: Mapped[list["Locality"]] = relationship(back_populates="lake", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Lake {self.name}>"


class Locality(Base):
    __tablename__ = "localities"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    habitat: Mapped[str | None] = mapped_column(Text, nullable=True)
    lake_id: Mapped[int | None] = mapped_column(
        ForeignKey("lakes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"), nullable=True, index=True
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    lake: Mapped["Lake | None"] = relationship(back_populates="localities", lazy="selectin")
    country: Mapped["Country | None"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<Locality {self.name}>"
