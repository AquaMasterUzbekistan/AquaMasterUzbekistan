"""Fish Images Search Handler.

Allows users to search for 5 to 10 strictly verified, high-quality images of any fish species
via Wikimedia Commons and iNaturalist APIs, supporting strict taxon parsing, multi-tier queries,
confidence levels (ANIQ MOSLIK, QISMAN MOSLIK, TASDIQLANMAGAN), and "Boshqa suratlarni izlash".
"""

from __future__ import annotations

import html
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    BufferedInputFile,
)

from app.localization import uz
from app.database.session import async_session
from app.services import AIService, FishService, FishImageSearchService, MatchConfidence, FishImageSearchResult

logger = logging.getLogger(__name__)

router = Router(name="fish_images")

# Concurrent request protection per user
_active_user_requests: set[int] = set()

# Seen images cache per user: user_id -> set of URLs seen in current search session
_user_seen_images: dict[int, set[str]] = {}
# Last query string per user
_user_last_query: dict[int, str] = {}
# Last species ID per user
_user_last_species_id: dict[int, int] = {}


class FishImageSearchState(StatesGroup):
    waiting_query = State()


def image_search_back_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown when waiting for fish name."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home")]
        ]
    )


def image_search_followup_keyboard(
    species_id: int | None = None,
    has_more: bool = True,
    is_query_mode: bool = False,
) -> InlineKeyboardMarkup:
    """Keyboard shown after search results with actions for more images or full dossier."""
    rows: list[list[InlineKeyboardButton]] = []

    # Row 1: More images
    if has_more:
        if species_id:
            rows.append([
                InlineKeyboardButton(
                    text="🔄 Boshqa suratlarni izlash",
                    callback_data=f"fish_images:more:{species_id}",
                )
            ])
        elif is_query_mode:
            rows.append([
                InlineKeyboardButton(
                    text="🔄 Boshqa suratlarni izlash",
                    callback_data="fish_images:more_q",
                )
            ])

    # Row 2: Full dossier and/or new search
    action_row: list[InlineKeyboardButton] = []
    if species_id:
        action_row.append(
            InlineKeyboardButton(
                text="📚 To‘liq ma’lumot",
                callback_data=f"profile:{species_id}:full_post",
            )
        )
    action_row.append(
        InlineKeyboardButton(text="🔎 Yana qidirish", callback_data="search_images")
    )
    rows.append(action_row)

    # Row 3: Return home or profile
    nav_row: list[InlineKeyboardButton] = []
    if species_id:
        nav_row.append(
            InlineKeyboardButton(
                text="◀️ Profilga qaytish",
                callback_data=f"profile:{species_id}:summary",
            )
        )
    nav_row.append(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))
    rows.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_verified_fish_images(
    target_message: Message,
    result: FishImageSearchResult,
    user_id: int,
    species_id: int | None = None,
    is_query_mode: bool = False,
) -> None:
    """Deliver verified fish images safely (handling 1 image vs media groups) with fallbacks."""
    # Build detailed metadata caption
    caption_lines: list[str] = []

    if result.confidence == MatchConfidence.EXACT:
        caption_lines.append(f"🎯 <b>ANIQ MOSLIK:</b> <b>{html.escape(result.resolved_name)}</b>")
    else:
        caption_lines.append(f"⚠️ <b>QISMAN MOSLIK:</b> <b>{html.escape(result.resolved_name)}</b>")

    caption_lines.append(f"🔎 Qidiruv: <i>{html.escape(result.query)}</i>")

    if result.confidence == MatchConfidence.PARTIAL and result.components and result.components.variant:
        caption_lines.append(
            f"💡 <i>Eslatma: Aniq «{html.escape(result.components.variant)}» varianti bo'yicha suratlar topilmadi. "
            f"Faqat tasdiqlangan <b>{html.escape(result.components.genus or '')}</b> avlodi suratlari keltirilmoqda.</i>"
        )

    caption_lines.append(f"\n📸 Tasdiqlangan suratlar: <b>{len(result.images)} ta</b>")
    caption_lines.append("🌐 <b>Manbalar va Litsenziyalar:</b>")

    for idx, img in enumerate(result.images, 1):
        short_author = html.escape(img.author[:35]) if img.author else ""
        author_str = f" — {short_author}" if short_author else ""
        caption_lines.append(
            f"{idx}. {html.escape(img.source)} ({html.escape(img.license)}){author_str}"
        )

    caption_text = "\n".join(caption_lines)
    if len(caption_text) > 1024:
        caption_text = caption_text[:1020] + "..."

    # Remember seen URLs for this user
    if user_id not in _user_seen_images:
        _user_seen_images[user_id] = set()
    for img in result.images:
        _user_seen_images[user_id].add(img.url)

    # 1. Single image: answer_photo
    if len(result.images) == 1:
        img_item = result.images[0]
        try:
            await target_message.answer_photo(
                photo=img_item.url,
                caption=caption_text,
                parse_mode="HTML",
            )
        except Exception as tg_err:
            logger.warning("Direct single photo send failed (%s). Attempting buffered fallback...", tg_err)
            img_bytes = await FishImageSearchService.download_image_bytes(img_item.url)
            if img_bytes:
                await target_message.answer_photo(
                    photo=BufferedInputFile(file=img_bytes, filename="fish.jpg"),
                    caption=caption_text,
                    parse_mode="HTML",
                )
            else:
                raise tg_err

    # 2. Multiple images (2-10): answer_media_group
    else:
        media_group: list[InputMediaPhoto] = []
        for i, img in enumerate(result.images):
            media_group.append(
                InputMediaPhoto(
                    media=img.url,
                    caption=caption_text if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
            )

        try:
            await target_message.answer_media_group(media=media_group)
        except Exception as tg_err:
            logger.warning(
                "Direct Telegram media group URL send failed (%s). "
                "Attempting safe buffered download fallback...",
                tg_err
            )
            buffered_group: list[InputMediaPhoto] = []
            for i, img in enumerate(result.images):
                img_bytes = await FishImageSearchService.download_image_bytes(img.url)
                if img_bytes:
                    buffered_group.append(
                        InputMediaPhoto(
                            media=BufferedInputFile(file=img_bytes, filename=f"fish_{i+1}.jpg"),
                            caption=caption_text if len(buffered_group) == 0 else None,
                            parse_mode="HTML" if len(buffered_group) == 0 else None,
                        )
                    )
            if buffered_group:
                await target_message.answer_media_group(media=buffered_group)
            else:
                raise tg_err

    # Send prompt with follow-up action buttons
    status_note = (
        "Aniq mos keladigan suratlar yuborildi."
        if result.confidence == MatchConfidence.EXACT
        else f"Faqat tasdiqlangan {result.components.genus if result.components else ''} suratlari yuborildi."
    )
    await target_message.answer(
        f"✅ {status_note}\n\nQuyidagi amallardan birini tanlang:",
        reply_markup=image_search_followup_keyboard(
            species_id=species_id,
            has_more=True,
            is_query_mode=is_query_mode,
        ),
    )


@router.callback_query(F.data == "search_images")
async def handle_search_images_entry(callback: CallbackQuery, state: FSMContext):
    """Handle legacy clicking '🔎 Baliq suratlarini qidirish' — redirect to unified search."""
    from app.handlers.search import SearchState
    from app.keyboards.search import search_main_keyboard
    await state.set_state(SearchState.waiting_query)
    await callback.message.edit_text(
        uz.SEARCH_PROMPT_MSG,
        reply_markup=search_main_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("images"))
async def handle_cmd_images(message: Message, state: FSMContext):
    """Handle /images command directly — redirect to unified search."""
    from app.handlers.search import SearchState
    from app.keyboards.search import search_main_keyboard
    await state.set_state(SearchState.waiting_query)
    await message.answer(
        uz.SEARCH_PROMPT_MSG,
        reply_markup=search_main_keyboard(),
        parse_mode="HTML",
    )


@router.message(FishImageSearchState.waiting_query, ~F.text.startswith("/"))
async def process_fish_image_query(message: Message, state: FSMContext):
    """Process fish name input and return strictly verified images."""
    user_id = message.from_user.id if message.from_user else 0
    raw_query = message.text.strip() if message.text else ""

    if not raw_query:
        await message.answer(
            "⚠️ Iltimos, baliq nomini matn shaklida yuboring.",
            reply_markup=image_search_back_keyboard(),
        )
        return

    # Clear image search waiting state now that query is submitted
    await state.clear()

    # Prevent concurrent flooding from same user
    if user_id in _active_user_requests:
        logger.warning("User %s attempted concurrent search query while busy", user_id)
        await message.answer(uz.IMG_SEARCH_BUSY, parse_mode="HTML")
        return

    _active_user_requests.add(user_id)
    _user_last_query[user_id] = raw_query
    _user_seen_images[user_id] = set()
    logger.info("PROCESSING_IMAGE_QUERY | user_id=%s | raw_query='%s'", user_id, raw_query)
    waiting_msg = await message.answer(uz.IMG_SEARCH_WAITING, parse_mode="HTML")

    try:
        async with async_session() as session:
            from app.repositories import UserRepository
            user_repo = UserRepository(session)
            await user_repo.log_activity(user_id, "image_search", raw_query)
            result = await FishImageSearchService.search_fish_images(
                query=raw_query,
                session=session,
                ai_service=None,
                max_images=8,
                user_id=user_id,
            )

        # Case 1: Unverified or No verified images found
        if not result or result.confidence == MatchConfidence.UNVERIFIED or not result.images:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="✍️ Taklif qoldirish", callback_data=f"suggest:fish:{raw_query[:30]}"))
            builder.row(InlineKeyboardButton(text="🔎 Qayta qidirish", callback_data="search"))
            builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))
            await waiting_msg.edit_text(
                uz.SEARCH_NOT_FOUND_MSG,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
            return

        # Clean up waiting message
        try:
            await waiting_msg.delete()
        except Exception:
            pass

        # Case 2: Verified images found
        await send_verified_fish_images(
            target_message=message,
            result=result,
            user_id=user_id,
            is_query_mode=True,
        )
    except Exception as e:
        logger.error(f"Image search query failed: {e}", exc_info=True)
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="✍️ Taklif qoldirish", callback_data=f"suggest:fish:{raw_query[:30]}"))
        builder.row(InlineKeyboardButton(text="🔎 Qayta qidirish", callback_data="search"))
        builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))
        await waiting_msg.edit_text(
            uz.SEARCH_NOT_FOUND_MSG,
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    finally:
        _active_user_requests.discard(user_id)


@router.callback_query(F.data.regexp(r"^fish_images:fetch:(\d+)$"))
async def handle_fetch_species_images(callback: CallbackQuery):
    """Fetch verified photos for a species from its catalog profile."""
    user_id = callback.from_user.id if callback.from_user else 0
    species_id = int(callback.data.split(":")[2])

    if user_id in _active_user_requests:
        await callback.answer(uz.IMG_SEARCH_BUSY, show_alert=True)
        return

    _active_user_requests.add(user_id)
    _user_last_species_id[user_id] = species_id
    _user_seen_images[user_id] = set()

    waiting_msg = await callback.message.answer(uz.IMG_SEARCH_WAITING, parse_mode="HTML")
    await callback.answer()

    try:
        async with async_session() as session:
            fish_svc = FishService(session)
            sp = await fish_svc.get_species(species_id)
            if not sp:
                await waiting_msg.edit_text(uz.ERROR_NOT_FOUND)
                return

            from app.repositories import UserRepository
            user_repo = UserRepository(session)
            await user_repo.log_activity(user_id, "image_search", sp.scientific_name)

            search_query = sp.scientific_name
            ai_service = AIService()
            result = await FishImageSearchService.search_fish_images(
                query=search_query,
                session=session,
                ai_service=ai_service,
                max_images=8,
                user_id=user_id,
            )

        if not result or not result.images:
            await waiting_msg.edit_text(
                f"❌ «<b>{html.escape(sp.scientific_name)}</b>» bo'yicha ishonchli suratlar topilmadi.",
                reply_markup=image_search_followup_keyboard(species_id=species_id, has_more=False),
                parse_mode="HTML",
            )
            return

        try:
            await waiting_msg.delete()
        except Exception:
            pass

        await send_verified_fish_images(
            target_message=callback.message,
            result=result,
            user_id=user_id,
            species_id=species_id,
            is_query_mode=False,
        )

    except Exception as e:
        logger.error("Error fetching images for species %s: %s", species_id, e, exc_info=True)
        try:
            await waiting_msg.edit_text(
                "⚠️ Suratlar qidirishda kutilmagan xatolik yuz berdi.",
                reply_markup=image_search_followup_keyboard(species_id=species_id, has_more=False),
            )
        except Exception:
            pass
    finally:
        _active_user_requests.discard(user_id)


@router.callback_query(F.data.regexp(r"^fish_images:more:(\d+)$"))
async def handle_more_species_images(callback: CallbackQuery):
    """Search for additional fresh photos for species, excluding previously seen URLs."""
    user_id = callback.from_user.id if callback.from_user else 0
    species_id = int(callback.data.split(":")[2])

    if user_id in _active_user_requests:
        await callback.answer(uz.IMG_SEARCH_BUSY, show_alert=True)
        return

    _active_user_requests.add(user_id)
    seen_urls = _user_seen_images.get(user_id, set())

    waiting_msg = await callback.message.answer(
        "🔄 <b>Yangi suratlar qidirilmoqda...</b>\n<i>Avval ko'rsatilgan suratlar takrorlanmaydi.</i>",
        parse_mode="HTML",
    )
    await callback.answer()

    try:
        async with async_session() as session:
            fish_svc = FishService(session)
            sp = await fish_svc.get_species(species_id)
            if not sp:
                await waiting_msg.edit_text(uz.ERROR_NOT_FOUND)
                return

            from app.repositories import UserRepository
            user_repo = UserRepository(session)
            await user_repo.log_activity(user_id, "image_search", f"more:{sp.scientific_name}")

            ai_service = AIService()
            result = await FishImageSearchService.search_fish_images(
                query=sp.scientific_name,
                session=session,
                ai_service=ai_service,
                max_images=8,
                user_id=user_id,
                seen_urls=seen_urls,
            )

        if not result or not result.images:
            await waiting_msg.edit_text(
                f"ℹ️ «<b>{html.escape(sp.scientific_name)}</b>» turi bo'yicha boshqa yangi tasdiqlangan suratlar topilmadi.\n\n"
                f"Oldinroq barcha mavjud sifatli suratlar taqdim etilgan.",
                reply_markup=image_search_followup_keyboard(species_id=species_id, has_more=False),
                parse_mode="HTML",
            )
            return

        try:
            await waiting_msg.delete()
        except Exception:
            pass

        await send_verified_fish_images(
            target_message=callback.message,
            result=result,
            user_id=user_id,
            species_id=species_id,
            is_query_mode=False,
        )

    except Exception as e:
        logger.error("Error fetching more images for species %s: %s", species_id, e, exc_info=True)
        try:
            await waiting_msg.edit_text(
                "⚠️ Yangi suratlar qidirishda xatolik yuz berdi.",
                reply_markup=image_search_followup_keyboard(species_id=species_id, has_more=False),
            )
        except Exception:
            pass
    finally:
        _active_user_requests.discard(user_id)


@router.callback_query(F.data == "fish_images:more_q")
async def handle_more_query_images(callback: CallbackQuery):
    """Search for additional fresh photos for the user's last text query."""
    user_id = callback.from_user.id if callback.from_user else 0
    query = _user_last_query.get(user_id, "")

    if not query:
        await callback.answer("Avval baliq nomini qidirishingiz kerak.", show_alert=True)
        return

    if user_id in _active_user_requests:
        await callback.answer(uz.IMG_SEARCH_BUSY, show_alert=True)
        return

    _active_user_requests.add(user_id)
    seen_urls = _user_seen_images.get(user_id, set())

    waiting_msg = await callback.message.answer(
        "🔄 <b>Yangi suratlar qidirilmoqda...</b>\n<i>Avval ko'rsatilgan suratlar takrorlanmaydi.</i>",
        parse_mode="HTML",
    )
    await callback.answer()

    try:
        ai_service = AIService()
        async with async_session() as session:
            from app.repositories import UserRepository
            user_repo = UserRepository(session)
            await user_repo.log_activity(user_id, "image_search", f"more:{query}")
            result = await FishImageSearchService.search_fish_images(
                query=query,
                session=session,
                ai_service=ai_service,
                max_images=8,
                user_id=user_id,
                seen_urls=seen_urls,
            )

        if not result or not result.images:
            await waiting_msg.edit_text(
                f"ℹ️ «<b>{html.escape(query)}</b>» bo'yicha boshqa yangi tasdiqlangan suratlar topilmadi.\n\n"
                f"Oldinroq barcha mavjud sifatli suratlar taqdim etilgan.",
                reply_markup=image_search_followup_keyboard(has_more=False, is_query_mode=True),
                parse_mode="HTML",
            )
            return

        try:
            await waiting_msg.delete()
        except Exception:
            pass

        await send_verified_fish_images(
            target_message=callback.message,
            result=result,
            user_id=user_id,
            species_id=None,
            is_query_mode=True,
        )

    except Exception as e:
        logger.error("Error fetching more images for query '%s': %s", query, e, exc_info=True)
        try:
            await waiting_msg.edit_text(
                "⚠️ Yangi suratlar qidirishda xatolik yuz berdi.",
                reply_markup=image_search_followup_keyboard(has_more=False, is_query_mode=True),
            )
        except Exception:
            pass
    finally:
        _active_user_requests.discard(user_id)
