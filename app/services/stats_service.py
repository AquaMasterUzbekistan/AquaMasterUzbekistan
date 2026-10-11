"""Services for breeding, health, articles, images, reports, stats."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    BreedingRepository, HealthRepository, ArticleRepository,
    ArticleCategoryRepository, DictionaryRepository, ImageRepository,
    ReportRepository, IdentificationRequestRepository,
    SpeciesRepository, UserRepository, LocalityRepository,
)
from app.models.species import Species
from app.models.image import SpeciesImage
from app.models.report import Report, ReportType, ReportStatus
from app.models.user import User


class BreedingService:
    def __init__(self, session: AsyncSession):
        self.repo = BreedingRepository(session)

    async def get_user_records(self, user_id: int):
        return await self.repo.get_by_user(user_id)

    async def create_record(self, user_id: int, species_id: int | None = None, **kwargs):
        return await self.repo.create(user_id=user_id, species_id=species_id, **kwargs)


class HealthService:
    def __init__(self, session: AsyncSession):
        self.repo = HealthRepository(session)

    async def get_all(self):
        return await self.repo.get_all_sorted()

    async def get_condition(self, condition_id: int):
        return await self.repo.get_by_id(condition_id)


class ArticleService:
    def __init__(self, session: AsyncSession):
        self.article_repo = ArticleRepository(session)
        self.category_repo = ArticleCategoryRepository(session)

    async def get_categories(self):
        return await self.category_repo.get_all_sorted()

    async def get_articles(self, category_id: int | None = None, limit: int = 20, offset: int = 0):
        if category_id:
            return await self.article_repo.get_by_category(category_id)
        return await self.article_repo.get_published(limit, offset)

    async def get_article(self, article_id: int):
        return await self.article_repo.get_by_id(article_id)


class ImageService:
    def __init__(self, session: AsyncSession):
        self.repo = ImageRepository(session)

    async def get_species_images(self, species_id: int):
        return await self.repo.get_by_species(species_id)

    async def add_image(self, species_id: int, **kwargs):
        return await self.repo.create(species_id=species_id, **kwargs)


class ReportService:
    def __init__(self, session: AsyncSession):
        self.repo = ReportRepository(session)

    async def submit_report(self, user_id: int, species_id: int | None,
                            report_type: str, description: str):
        return await self.repo.create(
            user_id=user_id,
            species_id=species_id,
            report_type=ReportType(report_type),
            description=description,
        )

    async def get_pending(self):
        return await self.repo.get_pending()

    async def resolve(self, report_id: int, admin_response: str):
        return await self.repo.update(
            report_id,
            status=ReportStatus.RESOLVED,
            admin_response=admin_response,
        )


class StatsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.species_repo = SpeciesRepository(session)
        self.user_repo = UserRepository(session)

    async def get_dashboard(self) -> dict:
        total_users = await self.user_repo.count()
        active_users = await self.user_repo.count_active()
        total_species = await self.species_repo.count()
        published_species = await self.species_repo.count_published()

        # Image count
        img_count_result = await self.session.execute(
            select(func.count()).select_from(SpeciesImage)
        )
        total_images = img_count_result.scalar_one()

        # Report count
        report_count_result = await self.session.execute(
            select(func.count()).select_from(Report).where(Report.status == "pending")
        )
        pending_reports = report_count_result.scalar_one()

        most_viewed = await self.species_repo.get_most_viewed(5)

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_species": total_species,
            "published_species": published_species,
            "total_images": total_images,
            "pending_reports": pending_reports,
            "most_viewed": most_viewed,
        }

    async def get_user_statistics(self) -> dict:
        """Calculate comprehensive user and activity metrics strictly in Asia/Tashkent timezone."""
        try:
            from zoneinfo import ZoneInfo
            tashkent_tz = ZoneInfo("Asia/Tashkent")
        except Exception:
            from datetime import timezone as dt_timezone, timedelta as dt_timedelta
            tashkent_tz = dt_timezone(dt_timedelta(hours=5), name="Asia/Tashkent")

        from datetime import datetime, timezone, timedelta
        from sqlalchemy import or_

        now_tashkent = datetime.now(tashkent_tz)
        today_start_tashkent = now_tashkent.replace(hour=0, minute=0, second=0, microsecond=0)
        today_start_utc = today_start_tashkent.astimezone(timezone.utc)
        today_start_naive = today_start_utc.replace(tzinfo=None)

        seven_days_ago_utc = (now_tashkent - timedelta(days=7)).astimezone(timezone.utc)
        seven_days_ago_naive = seven_days_ago_utc.replace(tzinfo=None)

        thirty_days_ago_utc = (now_tashkent - timedelta(days=30)).astimezone(timezone.utc)
        thirty_days_ago_naive = thirty_days_ago_utc.replace(tzinfo=None)

        # 1. Total users
        total_users = (
            await self.session.execute(select(func.count()).select_from(User))
        ).scalar_one()

        # 2. Joined today (since 00:00:00 Asia/Tashkent)
        stmt_today = select(func.count()).select_from(User).where(
            or_(User.created_at >= today_start_utc, User.created_at >= today_start_naive)
        )
        joined_today = (await self.session.execute(stmt_today)).scalar_one()

        # 3. Joined last 7 days
        stmt_7 = select(func.count()).select_from(User).where(
            or_(User.created_at >= seven_days_ago_utc, User.created_at >= seven_days_ago_naive)
        )
        joined_7 = (await self.session.execute(stmt_7)).scalar_one()

        # 4. Joined last 30 days
        stmt_30 = select(func.count()).select_from(User).where(
            or_(User.created_at >= thirty_days_ago_utc, User.created_at >= thirty_days_ago_naive)
        )
        joined_30 = (await self.session.execute(stmt_30)).scalar_one()

        # 5. Active in last 7 and 30 days
        stmt_act_7 = select(func.count()).select_from(User).where(
            or_(User.last_active_at >= seven_days_ago_utc, User.last_active_at >= seven_days_ago_naive)
        )
        active_7 = (await self.session.execute(stmt_act_7)).scalar_one()

        stmt_act_30 = select(func.count()).select_from(User).where(
            or_(User.last_active_at >= thirty_days_ago_utc, User.last_active_at >= thirty_days_ago_naive)
        )
        active_30 = (await self.session.execute(stmt_act_30)).scalar_one()

        # 6. Usage counts for features (search, image_search, full_info)
        search_count = await self.user_repo.get_action_count("search")
        image_search_count = await self.user_repo.get_action_count("image_search")
        full_info_count = await self.user_repo.get_action_count("full_info")

        return {
            "total_users": total_users,
            "joined_today": joined_today,
            "joined_7_days": joined_7,
            "joined_30_days": joined_30,
            "active_7_days": active_7,
            "active_30_days": active_30,
            "search_count": search_count,
            "image_search_count": image_search_count,
            "full_info_count": full_info_count,
            "calculated_at": now_tashkent.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def format_admin_stats_message(cls, stats: dict) -> str:
        """Format statistics cleanly for Telegram admin display."""
        return (
            "📊 <b>AQUAMASTER ATLAS — FOYDALANUVCHILAR STATISTIKASI</b>\n"
            f"<i>Vaqt mintaqasi: Asia/Tashkent ({stats.get('calculated_at', '')})</i>\n\n"
            "👥 <b>Foydalanuvchilar soni:</b>\n"
            f"• Jami ro'yxatdan o'tganlar: <b>{stats['total_users']} ta</b>\n"
            f"• Bugun qo'shilganlar: <b>{stats['joined_today']} ta</b>\n"
            f"• Oxirgi 7 kun ichida qo'shilganlar: <b>{stats['joined_7_days']} ta</b>\n"
            f"• Oxirgi 30 kun ichida qo'shilganlar: <b>{stats['joined_30_days']} ta</b>\n\n"
            "⚡ <b>Foydalanuvchilar faolligi:</b>\n"
            f"• Oxirgi 7 kunda faol bo'lganlar: <b>{stats['active_7_days']} ta</b>\n"
            f"• Oxirgi 30 kunda faol bo'lganlar: <b>{stats['active_30_days']} ta</b>\n\n"
            "🔥 <b>Bo'limlardan foydalanish statistikasi:</b>\n"
            f"• 🔎 Baliq qidirish so'rovlari: <b>{stats['search_count']} marta</b>\n"
            f"• 🖼️ Surat izlash so'rovlari: <b>{stats['image_search_count']} marta</b>\n"
            f"• 📚 To'liq ma'lumot (dosye) ko'rishlar: <b>{stats['full_info_count']} marta</b>\n\n"
            "🛡️ <i>Ma'lumotlar bazadagi haqiqiy faktik yozuvlar asosida hisoblandi.</i>"
        )
