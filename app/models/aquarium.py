"""User aquarium and fish collection models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Text, Integer, Float, DateTime,
    ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class UserAquarium(Base):
    __tablename__ = "user_aquariums"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    volume_liters: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="aquariums")
    fish: Mapped[list["UserFish"]] = relationship(
        back_populates="aquarium", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserAquarium {self.name}>"


class UserFish(Base):
    __tablename__ = "user_fish"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    aquarium_id: Mapped[int] = mapped_column(
        ForeignKey("user_aquariums.id", ondelete="CASCADE"), index=True
    )
    species_id: Mapped[int | None] = mapped_column(
        ForeignKey("species.id", ondelete="SET NULL"), nullable=True, index=True
    )
    custom_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity_male: Mapped[int] = mapped_column(Integer, default=0)
    quantity_female: Mapped[int] = mapped_column(Integer, default=0)
    quantity_unknown: Mapped[int] = mapped_column(Integer, default=0)
    date_acquired: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locality_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    aquarium: Mapped["UserAquarium"] = relationship(back_populates="fish")
    species: Mapped["Species | None"] = relationship(lazy="selectin")


from app.models.user import User  # noqa: E402, F401
from app.models.species import Species  # noqa: E402, F401
