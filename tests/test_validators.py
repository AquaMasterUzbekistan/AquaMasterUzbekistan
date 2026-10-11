"""Unit tests for validators and formatting utilities."""

from __future__ import annotations

from app.utils.validators import (
    is_valid_scientific_name,
    sanitize_search_query,
    is_positive_number,
    validate_telegram_id,
)
from app.utils.formatting import (
    format_water_params,
    format_aggression,
    format_difficulty,
    format_reliability,
)
from app.models.species import (
    Species,
    AggressionLevel,
    DifficultyLevel,
    ReliabilityLevel,
)


def test_scientific_name_validation():
    assert is_valid_scientific_name("Pseudotropheus demasoni") is True
    assert is_valid_scientific_name("Symphysodon discus") is True
    assert is_valid_scientific_name("Labidochromis caeruleus") is True
    assert is_valid_scientific_name("Demasoni") is False
    assert is_valid_scientific_name("") is False
    assert is_valid_scientific_name("123 456") is False


def test_search_query_sanitization():
    assert sanitize_search_query("  Discus  ") == "Discus"
    assert sanitize_search_query("select * from species;--") == "select * from species"
    assert sanitize_search_query("a" * 300) == "a" * 200


def test_number_validation():
    assert is_positive_number("123") is True
    assert is_positive_number("12.5") is True
    assert is_positive_number("0") is False
    assert is_positive_number("-5") is False
    assert is_positive_number("abc") is False


def test_telegram_id_validation():
    assert validate_telegram_id(123456789) is True
    assert validate_telegram_id(0) is False
    assert validate_telegram_id(-100) is False


def test_formatting_enums():
    assert "Tinch" in format_aggression(AggressionLevel.PEACEFUL)
    assert "Boshlang'ich" in format_difficulty(DifficultyLevel.BEGINNER)
    assert "Ilmiy manba bilan tasdiqlangan" in format_reliability(ReliabilityLevel.SCIENTIFIC)


def test_format_water_params():
    sp = Species(
        scientific_name="Pseudotropheus demasoni",
        genus_id=1,
        temp_min=24.0,
        temp_max=28.0,
        ph_min=7.8,
        ph_max=8.6,
        gh_min=10.0,
        gh_max=20.0,
        kh_min=8.0,
        kh_max=14.0,
    )
    formatted = format_water_params(sp)
    assert "24.0" in formatted and "28.0" in formatted
    assert "7.8" in formatted and "8.6" in formatted
    assert "10.0" in formatted and "20.0" in formatted
