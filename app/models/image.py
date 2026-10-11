"""Image models."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SAEnum, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class ImageType(str, enum.Enum):
    MAIN = "main"
    MALE = "male"
    FEMALE = "female"
    JUVENILE = "juvenile"
    ADULT = "adult"
    WILD = "wild"
    MORPH = "morph"
    HABITAT = "habitat"
    LOCALITY = "locality"
    OTHER = "other"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class SpeciesImage(Base):
    __tablename__ = "species_images"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), index=True
    )
    telegram_file_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    image_type: Mapped[ImageType] = mapped_column(
        SAEnum(ImageType), default=ImageType.MAIN
    )
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photographer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    license: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    verification: Mapped[VerificationStatus] = mapped_column(
        SAEnum(VerificationStatus), default=VerificationStatus.PENDING
    )
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    species: Mapped["Species"] = relationship(back_populates="images")

    def __repr__(self) -> str:
        return f"<SpeciesImage {self.id} type={self.image_type.value}>"


from app.models.species import Species  # noqa: E402, F401
