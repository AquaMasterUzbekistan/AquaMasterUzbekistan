"""User and role models."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, ForeignKey,
    Enum as SAEnum, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class RoleName(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    EDITOR = "editor"
    MODERATOR = "moderator"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[RoleName] = mapped_column(
        SAEnum(RoleName), default=RoleName.USER, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now(), nullable=False
    )

    # Relationships
    aquariums: Mapped[list["UserAquarium"]] = relationship(back_populates="user", lazy="selectin")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", lazy="selectin")
    recently_viewed: Mapped[list["RecentlyViewed"]] = relationship(back_populates="user", lazy="selectin")
    breeding_records: Mapped[list["BreedingRecord"]] = relationship(back_populates="user", lazy="selectin")
    reports: Mapped[list["Report"]] = relationship(back_populates="user", lazy="selectin")
    identification_requests: Mapped[list["IdentificationRequest"]] = relationship(
        back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} @{self.username}>"


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # search, image_search, full_info
    details: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user: Mapped["User | None"] = relationship(lazy="selectin")


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="favorites")
    species: Mapped["Species"] = relationship(lazy="selectin")


class RecentlyViewed(Base):
    __tablename__ = "recently_viewed"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"), index=True)
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="recently_viewed")
    species: Mapped["Species"] = relationship(lazy="selectin")


# Forward references resolved at import time via __init__.py
from app.models.aquarium import UserAquarium  # noqa: E402, F401
from app.models.breeding import BreedingRecord  # noqa: E402, F401
from app.models.report import Report, IdentificationRequest  # noqa: E402, F401
from app.models.species import Species  # noqa: E402, F401
