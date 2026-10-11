"""Async session factory and context manager."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.database.engine import engine

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Yield an async database session."""
    async with async_session() as session:
        return session
