"""AI Service for Fish Search, Explanation, and Vision Identification.

Uses ZenMux (Dots Studio) as primary engine, and Google Gemini API (gemini-3.8-flash)
as automatic high-speed fallback when ZenMux encounters errors or timeouts.

Grounded on trusted ichthyological databases:
FishBase.org, IUCN Red List, SeriouslyFish.com, Malawi.si, and Tanganyika.si.
"""

from __future__ import annotations

import base64
import json
import logging
import urllib.parse
from typing import Any

import aiohttp

from app.config.settings import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Siz akvarium baliqlari va chuchuk suv ixtiologiyasi bo'yicha dunyo miqyosidagi professional ekspert AI siz.
Barcha ma'lumotlaringiz quyidagi nufuzli, xalqaro va ilmiy manbalarga qat'iy tayanishi shart:
1. FishBase.org (Jahon baliqlar bazasi)
2. IUCN Red List (Xalqaro tabiatni muhofaza qilish ittifoqi)
3. SeriouslyFish.com (Professional akvarium profillari)
4. Malawi.si (Malavi ko'li biotoplari atlasi)
5. Tanganyika.si (Tanganika ko'li taksonomiyasi va biotoplari)

Qoidalar:
- Javobni chiroyli, tushunarli o'zbek tilida (lotin alifbosida), Telegram HTML formatida bering.
- Har doim barcha ochilgan HTML teglarini (masalan, <b> va </b>, <i> va </i>) to'g'ri yoping.
- Baliqlarning ilmiy nomlarini aniq lotin tilida yozing (hech qachon o'zbekchaga tarjima qilmang).
- Suv kimyosi (Harorat, pH, GH, KH, TDS) va oziqlantirish talablarini aniq raqamlarda ko'rsating.
- Har doim manba sifatida FishBase, IUCN, SeriouslyFish, Malawi.si yoki Tanganyika.si ni ko'rsating."""


class AIService:
    """Multi-provider AI client with ZenMux primary and Google Gemini fallback."""

    def __init__(self):
        self.zenmux_key = settings.AI_API_KEY
        self.zenmux_url = settings.AI_API_URL.rstrip("/")
        self.zenmux_model = settings.AI_MODEL

        self.google_key = settings.GOOGLE_API_KEY
        self.google_model = settings.GOOGLE_API_MODEL

    async def search_and_explain(self, query: str) -> str:
        """Search and provide encyclopedic fish explanation with automatic fallback."""
        user_prompt = f"""Foydalanuvchi qidirayotgan baliq haqida nufuzli manbalar (FishBase, IUCN, SeriouslyFish, Malawi.si, Tanganyika.si) asosida to'liq ensiklopedik ma'lumot bering:

Qidiruv so'rovi: "{query}"

Quyidagi tuzilmada batafsil ma'lumot bering:
🐟 <b>ILMIY NOMI:</b> <i>[Aniq lotincha ilmiy nomi]</i>
🏷️ <b>O'ZBEKCHA VA INGLIZCHA NOMI:</b> [Nomlari]
🔬 <b>TAKSONOMIYA:</b> Oila (Family), Jins (Genus)
🗺️ <b>TABIIY BIOTOP VA LOCALITY:</b> Ko'l/Daryo, mamlakat, yashash chuqurligi va biotop tavsifi (qoyali, qumli, o'simlikli)
🌡️ <b>SUV PARAMETRLARI:</b>
  • Harorat: ... °C
  • pH: ...
  • Qattiqlik (GH): ... dGH
  • Karbonat (KH): ... dKH
🏠 <b>AKVARIUM TALABLARI:</b> Baliq o'lchami (sm), minimal akvarium hajmi (L), suzish qatlami
⚔️ <b>XARAKTER VA MOSLIK:</b> Agressivlik darajasi, kimlar bilan birga yashay oladi va kimlar bilan taqiqlanadi
🍽️ <b>OZIQLANTIRISH (DIET):</b> Tabiiy ozuqasi, akvariumdagi ratsioni (o'txo'r/yirtqich, Malavi bloat xavfi bormi)
🥚 <b>KO'PAYISH:</b> Ko'payish turi (Mouthbrooder, Substrat, Cave spawner va h.k.)
📚 <b>ISHONCHLI MANBALAR:</b> FishBase.org, SeriouslyFish.com, IUCN, Malawi.si / Tanganyika.si"""

        # 1. Try ZenMux
        if self.zenmux_key:
            res = await self._call_zenmux_text(user_prompt)
            if res:
                return res
            logger.warning("ZenMux text search failed, switching to Google Gemini fallback...")

        # 2. Fallback to Google Gemini
        if self.google_key:
            res = await self._call_google_gemini_text(user_prompt)
            if res:
                return res

        return "⚠️ AI xizmatiga ulanishda xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring."

    async def identify_by_photo(self, photo_bytes: bytes, caption: str = "") -> str:
        """Identify fish from image bytes using Vision AI with automatic fallback."""
        prompt_text = (
            "Ushbu akvarium balig'i fotosuratini professional ixtiolog sifatida tahlil qiling.\n"
            "Tahlilda quyidagi manbalar mezonlaridan foydalaning: FishBase.org, SeriouslyFish.com, IUCN, Malawi.si, Tanganyika.si.\n"
            f"Foydalanuvchi izohi: '{caption}'\n\n"
            "Quyidagi tuzilmada aniq va to'liq javob bering:\n"
            "🔍 <b>ANIQLANGAN TUR:</b> <i>[Aniq ilmiy lotin nomi]</i> ([O'zbekcha/inglizcha nomi])\n"
            "📊 <b>ISHONCHLILIK:</b> [Masalan: 95%]\n"
            "👁️ <b>TANIQLILIK BELGILARI:</b> [Tana shakli, rang naqshlari, suzgichlar va ko'z tuzilishi tahlili]\n"
            "⚠️ <b>O'XSHASH TURLARDAN FARQI:</b> [Boshqa qaysi turlar bilan adashtirish mumkin emasligi]\n"
            "🗺️ <b>TABIIY LOCALITY VA BIOTOP:</b> [Ko'l/Daryo, davlat, biotop xaritasi]\n"
            "🧪 <b>SUV PARAMETRLARI:</b> Harorat (°C), pH, GH\n"
            "🏠 <b>AKVARIUM TALABLARI:</b> Hajm (L), xarakteri va qo'shnilari\n"
            "🍽️ <b>OZIQLANTIRISH:</b> Ratsion talabi (o'simlik/oqsil)\n"
            "📚 <b>MANBALAR:</b> FishBase.org, SeriouslyFish, IUCN, Malawi.si / Tanganyika.si"
        )

        # 1. Try ZenMux Vision (timeout 25s)
        if self.zenmux_key:
            res = await self._call_zenmux_vision(photo_bytes, prompt_text)
            if res:
                return res
            logger.warning("ZenMux vision failed or timed out, switching to Google Gemini Vision fallback...")

        # 2. Fallback to Google Gemini Vision
        if self.google_key:
            res = await self._call_google_gemini_vision(photo_bytes, prompt_text)
            if res:
                return res

        return "⚠️ Rasm tahlilida xatolik yuz berdi. Iltimos, qayta urinib ko'ring."

    # ── ZenMux Provider ─────────────────────────────────────────────────

    async def _call_zenmux_text(self, prompt: str) -> str | None:
        payload = {
            "model": self.zenmux_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }
        headers = {
            "Authorization": f"Bearer {self.zenmux_key}",
            "Content-Type": "application/json",
        }
        try:
            timeout = aiohttp.ClientTimeout(total=25)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.zenmux_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0]["message"]["content"]
                    else:
                        logger.error(f"ZenMux text error status={resp.status}")
        except Exception as e:
            logger.warning(f"ZenMux text request failed: {e}")
        return None

    async def _call_zenmux_vision(self, photo_bytes: bytes, prompt: str) -> str | None:
        b64_img = base64.b64encode(photo_bytes).decode("utf-8")
        payload = {
            "model": self.zenmux_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                        },
                    ],
                },
            ],
            "temperature": 0.3,
        }
        headers = {
            "Authorization": f"Bearer {self.zenmux_key}",
            "Content-Type": "application/json",
        }
        try:
            timeout = aiohttp.ClientTimeout(total=25)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.zenmux_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0]["message"]["content"]
                    else:
                        logger.error(f"ZenMux vision error status={resp.status}")
        except Exception as e:
            logger.warning(f"ZenMux vision request failed: {e}")
        return None

    # ── Google Gemini Provider ──────────────────────────────────────────

    async def _call_google_gemini_text(self, prompt: str) -> str | None:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.google_model}:generateContent?key={self.google_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4},
        }
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text")
                    else:
                        err_text = await resp.text()
                        logger.error(f"Google Gemini text error status={resp.status}: {err_text}")
        except Exception as e:
            logger.error(f"Google Gemini text request failed: {e}")
        return None

    async def _call_google_gemini_vision(self, photo_bytes: bytes, prompt: str) -> str | None:
        b64_img = base64.b64encode(photo_bytes).decode("utf-8")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.google_model}:generateContent?key={self.google_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_img,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.3},
        }
        try:
            timeout = aiohttp.ClientTimeout(total=35)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text")
                    else:
                        err_text = await resp.text()
                        logger.error(f"Google Gemini vision error status={resp.status}: {err_text}")
        except Exception as e:
            logger.error(f"Google Gemini vision request failed: {e}")
        return None

    # ── Wikipedia / Wikimedia Commons Image Resolver ────────────────────

    @staticmethod
    async def fetch_species_image_url(query: str) -> str | None:
        """Fetch encyclopedic fish photo from Wikipedia/Wikimedia Commons REST API."""
        try:
            clean_q = query.strip().split("(")[0].strip()
            encoded = urllib.parse.quote(clean_q)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
            headers = {"User-Agent": "AquaMasterBot/1.0 (contact@aquamaster.uz)"}
            timeout = aiohttp.ClientTimeout(total=6)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        thumb = data.get("thumbnail", {}).get("source")
                        original = data.get("originalimage", {}).get("source")
                        return thumb or original
        except Exception as e:
            logger.debug(f"Image fetch failed for query '{query}': {e}")
        return None
