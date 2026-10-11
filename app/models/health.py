"""Health conditions reference database."""

from __future__ import annotations

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, BigIntPK


class HealthCondition(Base):
    __tablename__ = "health_conditions"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    possible_causes: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    prevention: Mapped[str | None] = mapped_column(Text, nullable=True)
    important_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<HealthCondition {self.name_uz}>"
