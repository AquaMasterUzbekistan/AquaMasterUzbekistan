"""Dictionary / glossary terms."""

from __future__ import annotations

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, BigIntPK


class DictionaryTerm(Base):
    __tablename__ = "dictionary_terms"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    definition_uz: Mapped[str] = mapped_column(Text, nullable=False)
    definition_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"<DictionaryTerm {self.term}>"
