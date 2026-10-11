"""Knowledge Base Handler — 14 Essential Aquarium Guides (Section 8)."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.data.knowledge_base_data import KNOWLEDGE_ARTICLES
from app.keyboards.navigation import back_home_row

router = Router(name="knowledge")


@router.callback_query(F.data.in_(["knowledge_articles", "articles"]))
async def knowledge_menu(callback: CallbackQuery):
    """Show the list of 14 aquarium knowledge topics."""
    await _show_articles_list(callback.message, edit=True)
    await callback.answer()


@router.message(F.text == "/knowledge")
async def cmd_knowledge(message: Message):
    """Command /knowledge handler."""
    await _show_articles_list(message, edit=False)


async def _show_articles_list(message_obj, edit: bool = False, page: int = 1):
    per_page = 7
    total_pages = 2
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_items = KNOWLEDGE_ARTICLES[start_idx:end_idx]

    builder = InlineKeyboardBuilder()
    for item in current_items:
        builder.row(InlineKeyboardButton(
            text=f"{item['emoji']} {item['title']}",
            callback_data=f"know:view:{item['id']}"
        ))

    # Pagination buttons
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"know:page:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="➡️ Keyingi", callback_data=f"know:page:{page + 1}"))
    builder.row(*nav)

    builder.row(*back_home_row())

    text = (
        "📚 <b>AKVARIUM BILIMLARI ENSIKLOPEDIYASI</b>\n\n"
        "<i>Akvarium parvarishi, gidrokimyosi, filtratsiya va salomatlik bo'yicha to'liq amaliy qo'llanmalar:</i>\n\n"
        "O'qish uchun kerakli mavzuni tanlang:"
    )

    if edit and hasattr(message_obj, "edit_text"):
        await message_obj.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message_obj.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("know:page:"))
async def knowledge_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[2])
    await _show_articles_list(callback.message, edit=True, page=page)
    await callback.answer()


@router.callback_query(F.data.startswith("know:view:"))
async def knowledge_view(callback: CallbackQuery):
    article_id = int(callback.data.split(":")[2])
    article = next((a for a in KNOWLEDGE_ARTICLES if a["id"] == article_id), None)
    if not article:
        await callback.answer("Maqola topilmadi", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Bilimlar ro'yxatiga qaytish", callback_data="knowledge_articles"))
    builder.row(*back_home_row())

    await callback.message.edit_text(
        article["content"],
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()
