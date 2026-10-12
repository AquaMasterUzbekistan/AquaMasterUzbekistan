"""Tests for Aquarium Glossary (Atamalar lug'ati) and Bot Info (About with IPs)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.localization import uz
from app.keyboards.main_menu import main_menu_keyboard
from app.handlers.remaining import _show_dict_paged
from app.handlers.about_suggest import ABOUT_TEXT, get_about_keyboard


def test_main_menu_keyboard_has_bot_haqida_malumot():
    """Verify that main menu has 'ℹ️ Bot haqida ma'lumot' and '📖 Atamalar lug‘ati'."""
    kb = main_menu_keyboard()
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]

    assert "📖 Atamalar lug‘ati" in button_texts
    assert "dictionary" in button_callbacks
    assert "ℹ️ Bot haqida ma'lumot" in button_texts
    assert "about_suggest" in button_callbacks


def test_about_text_contains_websites_and_ips():
    """Verify that all requested fish websites with IP addresses are in ABOUT_TEXT."""
    text = uz.ABOUT_TEXT

    # Author and contact
    assert "@shoazizoff" in text
    assert "talab va takliflar" in text.lower() or "taklif" in text.lower()

    # Websites & IP addresses
    expected_sites = [
        ("malawi.si", "193.243.141.75"),
        ("tanganyika.si", "193.243.141.75"),
        ("fishbase", "193.10.57.58"),
        ("seriouslyfish.com", "188.114.97.11"),
        ("planetcatfish.com", "172.67.70.147"),
        ("cichlidae.com", "104.26.3.49"),
        ("scotcat.com", "208.113.159.23"),
        ("researcharchive.calacademy.org", "192.40.158.77"),
    ]

    for site, ip in expected_sites:
        assert site in text.lower(), f"Expected site '{site}' missing in ABOUT_TEXT"
        assert ip in text, f"Expected IP '{ip}' for site '{site}' missing in ABOUT_TEXT"


def test_about_keyboard_buttons():
    """Verify about keyboard has direct contact to @shoazizoff and suggestion button."""
    kb = get_about_keyboard().as_markup()
    urls = [btn.url for row in kb.inline_keyboard for btn in row if btn.url]
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]

    assert "https://t.me/shoazizoff" in urls
    assert "suggest:start" in callbacks


@pytest.mark.asyncio
async def test_show_dict_paged_executes_cleanly():
    """Verify that _show_dict_paged builds keyboard without NameError or unhandled exception."""
    mock_msg = MagicMock()
    mock_msg.edit_text = AsyncMock()

    await _show_dict_paged(mock_msg, page=1, edit=True)

    mock_msg.edit_text.assert_awaited_once()
    args, kwargs = mock_msg.edit_text.call_args
    rendered_text = args[0] if args else kwargs.get("text", "")
    rendered_kb = kwargs.get("reply_markup")

    assert "atamalar" in rendered_text.lower()
    assert rendered_kb is not None
    # Check that search button and term buttons exist
    btn_texts = [btn.text for row in rendered_kb.inline_keyboard for btn in row]
    assert any("qidirish" in b.lower() for b in btn_texts)
