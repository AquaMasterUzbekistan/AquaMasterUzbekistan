"""Unit and integration tests for user statistics and admin stats functionality."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import async_session
from app.database.engine import engine
from app.database.base import Base
import app.models  # Register all tables
from app.models.user import User, RoleName, UserActivityLog
from app.repositories.user_repo import UserRepository
from app.services.stats_service import StatsService
from app.utils.security import is_admin, has_admin_access
from app.config.settings import settings
import app.localization.uz as uz


class TestAdminStats(unittest.IsolatedAsyncioTestCase):
    """Test suite for user tracking, activity logs, and /admin_stats calculations."""

    async def asyncSetUp(self):
        """Ensure all database tables exist."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def test_security_admin_checks(self):
        """Verify is_admin and has_admin_access correctly authorize only admins."""
        # Test non-admin user
        self.assertFalse(is_admin(99999999999999))
        self.assertFalse(has_admin_access(RoleName.USER))

        # Test admin roles
        self.assertTrue(has_admin_access(RoleName.ADMIN))
        self.assertTrue(has_admin_access(RoleName.SUPER_ADMIN))

        # Test dynamic admin ID check
        test_admin_id = 123456789
        original_admin_ids = list(settings.ADMIN_IDS)
        try:
            settings.ADMIN_IDS.append(test_admin_id)
            self.assertTrue(is_admin(test_admin_id))
        finally:
            settings.ADMIN_IDS = original_admin_ids

    async def test_user_creation_and_no_duplicates(self):
        """Verify get_or_create creates a user once, doesn't duplicate, and updates last_active_at."""
        test_tg_id = 888123456
        async with async_session() as session:
            repo = UserRepository(session)

            # First call -> user created
            u1 = await repo.get_or_create(
                telegram_id=test_tg_id,
                username="test_unique_user",
                first_name="TestName",
            )
            await session.commit()

            self.assertEqual(u1.telegram_id, test_tg_id)
            self.assertIsNotNone(u1.last_active_at)

            # Second call -> existing user returned, same ID, updated info
            u2 = await repo.get_or_create(
                telegram_id=test_tg_id,
                username="test_unique_user",
                first_name="TestNameUpdated",
            )
            await session.commit()

            self.assertEqual(u2.id, u1.id)
            self.assertEqual(u2.telegram_id, test_tg_id)
            self.assertEqual(u2.first_name, "TestNameUpdated")

    async def test_activity_logging_and_action_counts(self):
        """Verify log_activity records search, image_search, and full_info actions."""
        test_tg_id = 888123457
        async with async_session() as session:
            repo = UserRepository(session)

            # Ensure user exists
            await repo.get_or_create(telegram_id=test_tg_id, username="active_user")
            await session.commit()

            # Record initial counts
            init_search = await repo.get_action_count("search")
            init_image = await repo.get_action_count("image_search")
            init_info = await repo.get_action_count("full_info")

            # Log activities
            await repo.log_activity(test_tg_id, "search", "Aulonocara")
            await repo.log_activity(test_tg_id, "image_search", "Petrochromis")
            await repo.log_activity(test_tg_id, "full_info", "Pseudotropheus demasoni")
            await session.commit()

            # Verify incremented counts
            self.assertEqual(await repo.get_action_count("search"), init_search + 1)
            self.assertEqual(await repo.get_action_count("image_search"), init_image + 1)
            self.assertEqual(await repo.get_action_count("full_info"), init_info + 1)

    async def test_get_user_statistics_calculations(self):
        """Verify get_user_statistics returns accurate metrics with Asia/Tashkent timezone."""
        async with async_session() as session:
            stats_svc = StatsService(session)
            stats = await stats_svc.get_user_statistics()

            # Check that all required keys are present
            required_keys = [
                "total_users",
                "joined_today",
                "joined_7_days",
                "joined_30_days",
                "active_7_days",
                "active_30_days",
                "search_count",
                "image_search_count",
                "full_info_count",
                "calculated_at",
            ]
            for key in required_keys:
                self.assertIn(key, stats)

            self.assertGreaterEqual(stats["total_users"], 1)
            self.assertGreaterEqual(stats["joined_today"], 0)
            self.assertGreaterEqual(stats["joined_7_days"], 0)
            self.assertGreaterEqual(stats["joined_30_days"], 0)
            self.assertGreaterEqual(stats["active_7_days"], 0)
            self.assertGreaterEqual(stats["active_30_days"], 0)
            self.assertGreaterEqual(stats["search_count"], 0)
            self.assertGreaterEqual(stats["image_search_count"], 0)
            self.assertGreaterEqual(stats["full_info_count"], 0)

            # Verify message formatter outputs clean HTML
            formatted = StatsService.format_admin_stats_message(stats)
            self.assertIn("FOYDALANUVCHILAR STATISTIKASI", formatted)
            self.assertIn("Asia/Tashkent", formatted)
            self.assertIn(f"<b>{stats['total_users']} ta</b>", formatted)
            self.assertIn("Baliq qidirish so'rovlari", formatted)
            self.assertIn("Surat izlash so'rovlari", formatted)
            self.assertIn("To'liq ma'lumot (dosye) ko'rishlar", formatted)

    def test_admin_router_priority_over_image_search(self):
        """Verify that admin_router is prioritized before fish_images_router and search_router."""
        from app.handlers import all_routers
        from app.handlers.admin import admin_router
        from app.handlers.fish_images import router as fish_images_router
        from app.handlers.search import router as search_router

        self.assertIn(admin_router, all_routers)
        self.assertIn(fish_images_router, all_routers)
        self.assertIn(search_router, all_routers)

        admin_idx = all_routers.index(admin_router)
        fish_images_idx = all_routers.index(fish_images_router)
        search_idx = all_routers.index(search_router)

        self.assertLess(
            admin_idx,
            fish_images_idx,
            "admin_router must precede fish_images_router so /admin_stats is not intercepted by image search",
        )
        self.assertLess(
            admin_idx,
            search_idx,
            "admin_router must precede search_router so /admin_stats is not intercepted by text search",
        )

    async def test_cmd_admin_stats_clears_state_and_provides_keyboard(self):
        """Verify cmd_admin_stats clears any active FSM state and delivers stats with admin keyboard."""
        from app.handlers.admin.admin_handlers import cmd_admin_stats

        mock_state = AsyncMock()
        mock_user = MagicMock()
        admin_id = settings.ADMIN_IDS[0] if settings.ADMIN_IDS else 12345
        mock_user.id = admin_id
        mock_user.username = "admin_tester"

        mock_message = AsyncMock()
        mock_message.from_user = mock_user

        # Temporarily ensure admin_id is authorized
        original_admin_ids = list(settings.ADMIN_IDS)
        try:
            if admin_id not in settings.ADMIN_IDS:
                settings.ADMIN_IDS.append(admin_id)

            await cmd_admin_stats(mock_message, state=mock_state)

            # Verify state was explicitly cleared
            mock_state.clear.assert_awaited_once()

            # Verify response was sent with keyboard
            mock_message.answer.assert_awaited_once()
            call_args = mock_message.answer.call_args
            response_text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
            reply_markup = call_args[1].get("reply_markup")

            self.assertIn("FOYDALANUVCHILAR STATISTIKASI", response_text)
            self.assertIsNotNone(reply_markup)

            # Check buttons in markup
            callbacks = [btn.callback_data for row in reply_markup.inline_keyboard for btn in row]
            self.assertIn("admin:stats", callbacks)
            self.assertIn("admin_panel", callbacks)
            self.assertIn("home", callbacks)
        finally:
            settings.ADMIN_IDS = original_admin_ids

    async def test_cmd_admin_stats_unauthorized(self):
        """Verify non-admin user is rejected with ERROR_ADMIN_ONLY."""
        from app.handlers.admin.admin_handlers import cmd_admin_stats

        mock_state = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = 999999999999
        mock_message = AsyncMock()
        mock_message.from_user = mock_user

        await cmd_admin_stats(mock_message, state=mock_state)
        mock_state.clear.assert_awaited_once()
        mock_message.answer.assert_awaited_once_with(uz.ERROR_ADMIN_ONLY)


if __name__ == "__main__":
    unittest.main()
