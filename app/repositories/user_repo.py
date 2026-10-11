"""User repository."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.user import User, Favorite, RecentlyViewed, UserActivityLog


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self, telegram_id: int, username: str | None = None,
        first_name: str | None = None, last_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        now_dt = datetime.now(timezone.utc)
        if user is None:
            user = await self.create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                last_active_at=now_dt,
            )
        else:
            needs_update = False
            if (
                user.username != username
                or user.first_name != first_name
                or user.last_name != last_name
                or user.language_code != language_code
            ):
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.language_code = language_code
                needs_update = True

            last_dt = user.last_active_at
            if last_dt is None:
                user.last_active_at = now_dt
                needs_update = True
            else:
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
                if (now_dt - last_dt).total_seconds() >= 60:
                    user.last_active_at = now_dt
                    needs_update = True

            if needs_update:
                await self.session.commit()
        return user

    async def update_last_activity(self, telegram_id: int) -> None:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            now_dt = datetime.now(timezone.utc)
            last_dt = user.last_active_at
            if last_dt is None:
                user.last_active_at = now_dt
                await self.session.commit()
            else:
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
                if (now_dt - last_dt).total_seconds() >= 60:
                    user.last_active_at = now_dt
                    await self.session.commit()

    async def log_activity(
        self, telegram_id: int, action_type: str, details: str | None = None
    ) -> UserActivityLog:
        user = await self.get_by_telegram_id(telegram_id)
        now_dt = datetime.now(timezone.utc)
        log_entry = UserActivityLog(
            telegram_id=telegram_id,
            user_id=user.id if user else None,
            action_type=action_type,
            details=details[:255] if details else None,
            created_at=now_dt,
        )
        self.session.add(log_entry)
        if user:
            user.last_active_at = now_dt
        await self.session.commit()
        return log_entry

    async def get_action_count(self, action_type: str) -> int:
        stmt = (
            select(func.count())
            .select_from(UserActivityLog)
            .where(UserActivityLog.action_type == action_type)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def add_favorite(self, user_id: int, species_id: int) -> Favorite:
        fav = Favorite(user_id=user_id, species_id=species_id)
        self.session.add(fav)
        await self.session.commit()
        return fav

    async def remove_favorite(self, user_id: int, species_id: int) -> bool:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.species_id == species_id,
        )
        result = await self.session.execute(stmt)
        fav = result.scalar_one_or_none()
        if fav:
            await self.session.delete(fav)
            await self.session.commit()
            return True
        return False

    async def is_favorite(self, user_id: int, species_id: int) -> bool:
        stmt = select(func.count()).select_from(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.species_id == species_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_favorites(self, user_id: int) -> list[Favorite]:
        stmt = (
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_recently_viewed(self, user_id: int, species_id: int) -> None:
        # Keep only last 20
        rv = RecentlyViewed(user_id=user_id, species_id=species_id)
        self.session.add(rv)
        await self.session.commit()

    async def get_recently_viewed(self, user_id: int, limit: int = 20) -> list[RecentlyViewed]:
        stmt = (
            select(RecentlyViewed)
            .where(RecentlyViewed.user_id == user_id)
            .order_by(RecentlyViewed.viewed_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        stmt = select(func.count()).select_from(User).where(User.is_banned == False)  # noqa: E712
        result = await self.session.execute(stmt)
        return result.scalar_one()
