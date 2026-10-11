"""Aquarium calculator service."""

from __future__ import annotations

import math


class CalculatorService:
    """Stateless calculator — no DB required."""

    @staticmethod
    def volume(length_cm: float, width_cm: float, height_cm: float) -> float:
        """Calculate aquarium volume in liters."""
        return round((length_cm * width_cm * height_cm) / 1000, 1)

    @staticmethod
    def water_change(total_liters: float, percent: float) -> float:
        """Calculate water change amount in liters."""
        return round(total_liters * (percent / 100), 1)

    @staticmethod
    def heater_wattage(liters: float) -> str:
        """Estimate heater wattage needed."""
        # General rule: ~1 W per liter for moderate climate difference
        watts = math.ceil(liters)
        if watts <= 25:
            return "25 W"
        elif watts <= 50:
            return "50 W"
        elif watts <= 100:
            return "100 W"
        elif watts <= 150:
            return "150 W"
        elif watts <= 200:
            return "200 W"
        elif watts <= 300:
            return "300 W"
        else:
            count = math.ceil(watts / 300)
            return f"{count} × 300 W"

    @staticmethod
    def filter_flow(liters: float, turnover: int = 4) -> float:
        """Recommended filter flow rate (L/h)."""
        return round(liters * turnover, 0)

    @staticmethod
    def air_pump(liters: float) -> float:
        """Air pump output estimate (L/h)."""
        # ~1 L/h per liter of aquarium
        return round(liters, 0)

    @staticmethod
    def stocking_estimate(liters: float, avg_fish_size_cm: float = 5.0) -> int:
        """Rough fish stocking estimate."""
        # General guideline: 1 cm fish per 1-2 liters (conservative)
        if avg_fish_size_cm <= 0:
            avg_fish_size_cm = 5.0
        return max(1, int(liters / (avg_fish_size_cm * 2)))

    @staticmethod
    def salt_dosage(liters: float, target_ppt: float = 1.0) -> float:
        """Grams of salt needed."""
        return round(liters * target_ppt, 1)

    @staticmethod
    def feeding_estimate(fish_count: int, avg_size_cm: float = 5.0) -> str:
        """Rough daily feeding amount."""
        # ~2-3% body weight; approximate
        if fish_count <= 0:
            return "Ma'lumot yetarli emas."
        grams = round(fish_count * avg_size_cm * 0.02, 1)
        return f"~{grams} g/kun (taxminiy)"
