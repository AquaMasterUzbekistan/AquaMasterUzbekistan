"""Admin panel handlers."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.localization import uz
from app.keyboards import admin_menu_keyboard
from app.keyboards.navigation import back_home_row
from app.database.session import async_session
from app.repositories import UserRepository
from app.utils.security import has_admin_access, is_admin

router = Router(name="admin")


class AdminAddSpeciesState(StatesGroup):
    scientific_name = State()
    genus_id = State()


async def _check_admin(callback: CallbackQuery) -> bool:
    """Check if user has admin access."""
    user_id = callback.from_user.id if callback.from_user else 0
    if is_admin(user_id):
        return True
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(user_id)
        if not db_user or not has_admin_access(db_user.role):
            await callback.answer(uz.ERROR_ADMIN_ONLY, show_alert=True)
            return False
    return True


@router.message(Command("admin_stats"))
@router.message(F.text == "/admin_stats")
async def cmd_admin_stats(message: Message, state: FSMContext | None = None):
    """Admin-only user statistics dashboard."""
    if state:
        await state.clear()

    user_id = message.from_user.id if message.from_user else 0

    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(user_id)

        authorized = is_admin(user_id) or (db_user and has_admin_access(db_user.role))
        if not authorized:
            await message.answer(uz.ERROR_ADMIN_ONLY)
            return

        from app.services.stats_service import StatsService
        stats_svc = StatsService(session)
        stats = await stats_svc.get_user_statistics()
        text = StatsService.format_admin_stats_message(stats)

        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin:stats"))
        builder.row(InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel"))
        builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))

        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "admin:stats")
async def admin_stats_callback(callback: CallbackQuery, state: FSMContext | None = None):
    """Callback for admin stats from admin menu."""
    if state:
        await state.clear()

    if not await _check_admin(callback):
        return

    async with async_session() as session:
        from app.services.stats_service import StatsService
        stats_svc = StatsService(session)
        stats = await stats_svc.get_user_statistics()
        text = StatsService.format_admin_stats_message(stats)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin:stats"))
    builder.row(InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.message(Command("admin"))
@router.message(F.text == "/admin")
async def admin_command(message: Message, state: FSMContext | None = None):
    if state:
        await state.clear()

    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        async with async_session() as session:
            user_repo = UserRepository(session)
            db_user = await user_repo.get_by_telegram_id(user_id)
            if not db_user or not has_admin_access(db_user.role):
                await message.answer(uz.ERROR_ADMIN_ONLY)
                return

    await message.answer(uz.ADMIN_PANEL, reply_markup=admin_menu_keyboard(), parse_mode="HTML")


@router.message(Command("audit"))
@router.message(F.text == "/audit")
async def audit_command(message: Message, state: FSMContext | None = None):
    if state:
        await state.clear()
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(message.from_user.id)
        if not db_user or not has_admin_access(db_user.role):
            await message.answer(uz.ERROR_ADMIN_ONLY)
            return

        from app.services.audit_service import AuditService
        audit_svc = AuditService(session)
        report = await audit_svc.run_full_audit()
        text = audit_svc.format_audit_markdown(report)

    await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "admin:audit")
async def admin_audit_callback(callback: CallbackQuery):
    if not await _check_admin(callback):
        return

    async with async_session() as session:
        from app.services.audit_service import AuditService
        audit_svc = AuditService(session)
        report = await audit_svc.run_full_audit()
        text = audit_svc.format_audit_markdown(report)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Qayta hisoblash", callback_data="admin:audit"))
    builder.row(InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel"))
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:sync_db")
async def admin_sync_db_callback(callback: CallbackQuery):
    if not await _check_admin(callback):
        return

    await callback.answer("⏳ Baza sinxronlanmoqda...", show_alert=False)

    from app.services.ingestion_service import IngestionService
    from app.services.audit_service import AuditService
    from app.data import (
        MALAWI_GENERA, MALAWI_SPECIES,
        TANGANYIKA_GENERA, TANGANYIKA_SPECIES,
        VICTORIA_AFRICA_GENERA, VICTORIA_AFRICA_SPECIES,
        AMERICAN_GENERA, AMERICAN_SPECIES,
        OTHER_FRESHWATER_GENERA, OTHER_FRESHWATER_SPECIES,
    )

    async with async_session() as session:
        ingestion = IngestionService(session)
        fam_map = await ingestion.ensure_families()
        g_map = await ingestion.ingest_genera(MALAWI_GENERA, fam_map)
        g_map.update(await ingestion.ingest_genera(TANGANYIKA_GENERA, fam_map))
        g_map.update(await ingestion.ingest_genera(VICTORIA_AFRICA_GENERA, fam_map))
        g_map.update(await ingestion.ingest_genera(AMERICAN_GENERA, fam_map))
        g_map.update(await ingestion.ingest_genera(OTHER_FRESHWATER_GENERA, fam_map))

        await ingestion.ingest_species_batch(MALAWI_SPECIES, g_map, category_hint="Afrika Cichlidlari")
        await ingestion.ingest_species_batch(TANGANYIKA_SPECIES, g_map, category_hint="Afrika Cichlidlari")
        await ingestion.ingest_species_batch(VICTORIA_AFRICA_SPECIES, g_map, category_hint="Afrika Cichlidlari")
        await ingestion.ingest_species_batch(AMERICAN_SPECIES, g_map, category_hint="Amerika Cichlidlari")
        await ingestion.ingest_species_batch(OTHER_FRESHWATER_SPECIES, g_map, category_hint="Boshqa Baliqlar")

        audit_svc = AuditService(session)
        report = await audit_svc.run_full_audit()

    text = (
        f"✅ <b>Baza muvaffaqiyatli sinxronlandi!</b>\n\n"
        f"• Yangi turlar: {ingestion.report.new_species}\n"
        f"• Yangilangan turlar: {ingestion.report.updated_species}\n"
        f"• Duplikatlar filtri: {ingestion.report.duplicates_prevented}\n"
        f"• Jami faol turlar: {report.total_species}\n"
        f"• Tasdiqlangan rasmlar: {report.verified_images}\n"
        f"• To'liqlik ko'rsatkichi: {report.overall_completeness_pct}%\n"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Auditni ko'rish", callback_data="admin:audit"))
    builder.row(InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel"))
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")





@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if not await _check_admin(callback):
        return
    await callback.message.edit_text(uz.ADMIN_PANEL, reply_markup=admin_menu_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:add_species")
async def admin_add_species_start(callback: CallbackQuery, state: FSMContext):
    if not await _check_admin(callback):
        return
    await callback.message.edit_text(
        "➕ <b>Yangi tur qo'shish</b>\n\nIlmiy nomini kiriting (masalan: Pseudotropheus demasoni):",
        parse_mode="HTML",
    )
    await state.set_state(AdminAddSpeciesState.scientific_name)
    await callback.answer()


@router.message(AdminAddSpeciesState.scientific_name)
async def admin_add_species_name(message: Message, state: FSMContext):
    sci_name = message.text.strip()
    await state.clear()

    from app.utils.validators import is_valid_scientific_name
    if not is_valid_scientific_name(sci_name):
        await message.answer("⚠️ Noto'g'ri ilmiy nom formati. Kamida 2 so'z bo'lishi kerak.")
        return

    async with async_session() as session:
        from app.repositories import SpeciesRepository
        species_repo = SpeciesRepository(session)
        existing = await species_repo.get_by_scientific_name(sci_name)
        if existing:
            await message.answer(f"⚠️ Bu tur allaqachon mavjud: {sci_name}")
            return

        # Create with minimal data — admin will fill in details later
        from app.models.species import Species, ReliabilityLevel
        sp = Species(
            scientific_name=sci_name,
            genus_id=1,  # Default — admin should update
            reliability=ReliabilityLevel.UNVERIFIED,
            is_published=False,
        )
        session.add(sp)
        await session.commit()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel"))
    builder.row(*back_home_row())

    await message.answer(
        f"✅ Tur qo'shildi: <b>{sci_name}</b>\n\n"
        f"⚠️ Tur nashr qilinmagan va 🔴 Tasdiqlanmagan sifatida belgilangan.\n"
        f"Tahrirlash uchun admin paneldan foydalaning.",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin:reports")
async def admin_reports(callback: CallbackQuery):
    if not await _check_admin(callback):
        return

    async with async_session() as session:
        from app.services import ReportService
        svc = ReportService(session)
        reports = await svc.get_pending()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    if reports:
        for r in reports:
            label = f"📋 #{r.id} — {r.report_type.value}"
            builder.row(InlineKeyboardButton(text=label, callback_data=f"admin_report:{r.id}"))
    else:
        pass

    builder.row(InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel"))
    builder.row(*back_home_row())

    text = f"📋 <b>Xabarlar</b> ({len(reports)} ta kutilmoqda)"
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# Placeholder handlers for other admin actions
@router.callback_query(F.data.in_({"admin:edit_species", "admin:delete_species",
                                    "admin:add_image", "admin:articles",
                                    "admin:users", "admin:identifications"}))
async def admin_placeholder(callback: CallbackQuery):
    if not await _check_admin(callback):
        return
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel"))
    builder.row(*back_home_row())

    await callback.message.edit_text(
        "🔧 Bu bo'lim ishlab chiqilmoqda...",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()
