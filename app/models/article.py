"""Article and educational content models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Text, Boolean, DateTime,
    ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BigIntPK


class ArticleCategory(Base):
    __tablename__ = "article_categories"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)

    articles: Mapped[list["Article"]] = relationship(back_populates="category", lazy="selectin")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    cover_telegram_file_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("article_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped["ArticleCategory | None"] = relationship(back_populates="articles")

    def __repr__(self) -> str:
        return f"<Article {self.title}>"
