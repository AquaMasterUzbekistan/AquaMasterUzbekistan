"""SQLAlchemy declarative base."""

from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import DeclarativeBase

# BigIntPK uses Integer on SQLite (which is 64-bit and supports AUTOINCREMENT)
# and BigInteger on PostgreSQL.
BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass
