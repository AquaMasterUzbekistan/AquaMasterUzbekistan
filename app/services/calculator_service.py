"""Aquarium calculator service — 7 essential calculations (Section 9)."""

from __future__ import annotations

import math
from typing import Any


class CalculatorService:
    """Stateless calculator implementing all 7 Master Prompt requirements."""

    # 1. Akvarium hajmi (L x W x H)
    @staticmethod
    def volume(length_cm: float, width_cm: float, height_cm: float) -> float:
        """Calculate gross aquarium volume in liters."""
        return round((length_cm * width_cm * height_cm) / 1000, 1)

    # 2. Taxminiy haqiqiy suv hajmi (minus dekor/substrat)
    @staticmethod
    def net_water_volume(gross_liters: float, displacement_percent: float = 15.0) -> dict[str, Any]:
        """Calculate net water volume taking substrate, rocks, and equipment into account."""
        displacement_percent = max(0.0, min(50.0, displacement_percent))
        displaced_liters = round(gross_liters * (displacement_percent / 100), 1)
        net_liters = round(gross_liters - displaced_liters, 1)
        return {
            "gross_liters": gross_liters,
            "displacement_percent": displacement_percent,
            "displaced_liters": displaced_liters,
            "net_liters": net_liters,
        }

    # 3. Suv almashtirish hajmi (% -> litr)
    @staticmethod
    def water_change(total_liters: float, percent: float) -> float:
        """Calculate water change amount in liters."""
        return round(total_liters * (percent / 100), 1)

    # 4. Filtrning nominal oqimi va soatiga suv aylanishi (Turnover rate)
    @staticmethod
    def filter_turnover(pump_lph: float, tank_liters: float) -> dict[str, Any]:
        """Calculate filter turnover rate and assessment."""
        if tank_liters <= 0:
            return {"turnover": 0.0, "status": "Noto'g'ri hajm", "advice": ""}

        turnover = round(pump_lph / tank_liters, 1)
        if turnover < 3.0:
            status = "⚠️ Yetarli emas"
            advice = "Oqim past. Faqat kam sonli, tinch o'simlikli akvariumlar uchun mos."
        elif turnover <= 6.0:
            status = "✅ Normal / Maqbul"
            advice = "Oddiy tropik umumiy akvariumlar (Tetra, Skalyariya, Guppi) uchun optimal."
        elif turnover <= 10.0:
            status = "⚡ Kuchli / A'lo"
            advice = "Afrika cichlidlari (Malawi, Tanganyika), katta plecolar va yirik turlar uchun tavsiya etiladi."
        else:
            status = "🌊 O'ta kuchli"
            advice = "Daryo oqimi biotoplari uchun mos; mayda sekin suzuvchi baliqlarni charchatib qo'yishi mumkin."

        return {
            "pump_lph": pump_lph,
            "tank_liters": tank_liters,
            "turnover": turnover,
            "status": status,
            "advice": advice,
        }

    # 5. Kerakli suv miqdori va almashtirish jadvali
    @staticmethod
    def water_change_schedule(tank_liters: float, bioload: str = "medium") -> dict[str, Any]:
        """Recommended water change schedule based on bioload."""
        schedules = {
            "low": {
                "name": "Past yuklama (Kam sonli mayda baliqlar / O'simlikli)",
                "percent": 20,
                "interval_days": 10,
                "note": "Har 10 kunda bir marta almashtirish tavsiya etiladi.",
            },
            "medium": {
                "name": "O'rtacha yuklama (Standart jamoat akvariumi)",
                "percent": 25,
                "interval_days": 7,
                "note": "Haftada 1 marta muntazam almashtirish tavsiya etiladi.",
            },
            "high": {
                "name": "Yuqori yuklama (Cichlidlar, Diskuslar, Yirtqichlar)",
                "percent": 35,
                "interval_days": 7,
                "note": "Haftada 1 marta (yoki haftasiga 2 marta 20% dan) almashtirish shart.",
            },
        }
        cfg = schedules.get(bioload, schedules["medium"])
        liters_to_change = round(tank_liters * (cfg["percent"] / 100), 1)

        return {
            "bioload_name": cfg["name"],
            "percent": cfg["percent"],
            "interval_days": cfg["interval_days"],
            "liters_to_change": liters_to_change,
            "note": cfg["note"],
        }

    # 6. Ozuqa miqdori bo‘yicha yordamchi tavsiyalar
    @staticmethod
    def feeding_advice(fish_count: int, avg_size_cm: float = 6.0) -> dict[str, Any]:
        """Practical feeding guidelines based on biomass estimation and 2-3 minute rule."""
        if fish_count <= 0:
            return {"daily_grams": 0.0, "advice": "Baliqlar soni kiritilmagan."}

        # Rough biomass approximation (~2% daily requirement)
        daily_grams = round(fish_count * avg_size_cm * 0.02, 1)

        advice = (
            f"📊 <b>Kunlik taxminiy ozuqa:</b> ~{daily_grams} gramm (barcha baliqlar uchun jami)\n\n"
            "📌 <b>Amaliy qoidalar:</b>\n"
            "• <b>2–3 daqiqa qoidasi:</b> Baliqlar barcha berilgan ozuqani 2 daqiqada to'liq yeb tugatishi kerak. "
            "Tubga cho'kib qolgan har qanday ozuqa suvni zaharlaydi.\n"
            "• <b>Chastota:</b> Katta baliqlarga kuniga 1 yoki 2 marta oz-ozdan.\n"
            "• <b>Ochlik kuni:</b> Haftada 1 kun baliqlarga ovqat bermaslik ularning oshqozon-ichak yo'lini tozalaydi."
        )
        return {
            "daily_grams": daily_grams,
            "advice": advice,
        }

    # 7. Elektr energiyasi sarfi
    @staticmethod
    def electricity_consumption(
        filter_watts: float = 15.0,
        heater_watts: float = 100.0,
        heater_hours_day: float = 8.0,
        light_watts: float = 20.0,
        light_hours_day: float = 8.0,
        tariff_som_kwh: float = 450.0,
    ) -> dict[str, Any]:
        """Calculate daily and monthly power consumption (kWh) and approximate cost in Uzbek Som."""
        # Filter runs 24 hours
        filter_daily_kwh = (filter_watts * 24) / 1000
        heater_daily_kwh = (heater_watts * heater_hours_day) / 1000
        light_daily_kwh = (light_watts * light_hours_day) / 1000

        total_daily_kwh = round(filter_daily_kwh + heater_daily_kwh + light_daily_kwh, 2)
        total_monthly_kwh = round(total_daily_kwh * 30, 1)
        monthly_cost_som = int(total_monthly_kwh * tariff_som_kwh)

        return {
            "total_daily_kwh": total_daily_kwh,
            "total_monthly_kwh": total_monthly_kwh,
            "tariff_som": tariff_som_kwh,
            "monthly_cost_som": monthly_cost_som,
            "breakdown": {
                "filter": round(filter_daily_kwh * 30, 1),
                "heater": round(heater_daily_kwh * 30, 1),
                "light": round(light_daily_kwh * 30, 1),
            },
        }

    # Legacy helper methods preserved
    @staticmethod
    def heater_wattage(liters: float) -> str:
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
            return f"{math.ceil(watts / 300)} × 300 W"

    @staticmethod
    def filter_flow(liters: float, turnover: int = 4) -> float:
        return round(liters * turnover, 0)

    @staticmethod
    def air_pump(liters: float) -> float:
        return round(liters, 0)

    @staticmethod
    def stocking_estimate(liters: float, avg_fish_size_cm: float = 5.0) -> int:
        if avg_fish_size_cm <= 0:
            avg_fish_size_cm = 5.0
        return max(1, int(liters / (avg_fish_size_cm * 2)))

    @staticmethod
    def salt_dosage(liters: float, target_ppt: float = 1.0) -> float:
        return round(liters * target_ppt, 1)

    @staticmethod
    def feeding_estimate(fish_count: int, avg_size_cm: float = 5.0) -> str:
        if fish_count <= 0:
            return "Ma'lumot yetarli emas."
        grams = round(fish_count * avg_size_cm * 0.02, 1)
        return f"~{grams} g/kun (taxminiy)"
