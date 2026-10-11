"""Text formatting helpers for Telegram messages."""

from __future__ import annotations

from app.models.species import (
    Species, ReliabilityLevel, AggressionLevel,
    DifficultyLevel, BreedingType, OriginType,
)
from app.localization import uz


def format_reliability(level: ReliabilityLevel | None) -> str:
    """Return the Uzbek reliability badge."""
    if level is None:
        return uz.RELIABILITY.get("scientific", "🟢 Ilmiy manba bilan tasdiqlangan")
    val = level.value if hasattr(level, "value") else str(level)
    return uz.RELIABILITY.get(val, val)


def format_aggression(level: AggressionLevel | None) -> str:
    mapping = {
        AggressionLevel.PEACEFUL: "🕊️ Tinch",
        AggressionLevel.SEMI_AGGRESSIVE: "⚡ O'rtacha agressiv",
        AggressionLevel.AGGRESSIVE: "⚔️ Agressiv",
        AggressionLevel.HIGHLY_AGGRESSIVE: "🔥 Juda agressiv",
    }
    return mapping.get(level, uz.DATA_INSUFFICIENT) if level else uz.DATA_INSUFFICIENT


def format_difficulty(level: DifficultyLevel | None) -> str:
    mapping = {
        DifficultyLevel.BEGINNER: "🟢 Boshlang'ich",
        DifficultyLevel.INTERMEDIATE: "🟡 O'rtacha",
        DifficultyLevel.ADVANCED: "🟠 Ilg'or",
        DifficultyLevel.EXPERT: "🔴 Ekspert",
    }
    return mapping.get(level, uz.DATA_INSUFFICIENT) if level else uz.DATA_INSUFFICIENT


def format_breeding_type(bt: BreedingType | None) -> str:
    mapping = {
        BreedingType.MOUTHBROODER: "Og'izda tuxum saqlash (Mouthbrooder)",
        BreedingType.SUBSTRATE_SPAWNER: "Substratga tuxum qo'yish",
        BreedingType.CAVE_SPAWNER: "G'orda tuxum qo'yish",
        BreedingType.SHELL_SPAWNER: "Chig'anoqda tuxum qo'yish",
        BreedingType.BUBBLE_NEST: "Ko'pik uyasi",
        BreedingType.EGG_SCATTERER: "Tuxum sochish",
        BreedingType.LIVEBEARER: "Tirik tug'ish",
        BreedingType.OTHER: "Boshqa",
    }
    return mapping.get(bt, uz.DATA_INSUFFICIENT) if bt else uz.DATA_INSUFFICIENT


def format_origin(origin: OriginType | None) -> str:
    mapping = {
        OriginType.WILD: "🌿 Yovvoyi (Wild)",
        OriginType.TANK_BRED: "🏠 Akvariumda ko'paytirilgan",
        OriginType.SELECTIVE: "🧬 Seleksiya",
        OriginType.HYBRID: "🔀 Gibrid",
    }
    return mapping.get(origin, uz.DATA_INSUFFICIENT) if origin else uz.DATA_INSUFFICIENT


def format_range(min_val: float | None, max_val: float | None, unit: str = "") -> str:
    """Format a numeric range like '24-28 °C'."""
    if min_val is not None and max_val is not None:
        return f"{min_val}–{max_val} {unit}".strip()
    if min_val is not None:
        return f"{min_val}+ {unit}".strip()
    if max_val is not None:
        return f"≤{max_val} {unit}".strip()
    return uz.DATA_INSUFFICIENT


def format_fish_profile_summary(sp: Species) -> str:
    """Page 1 strictly text-only summary of a fish profile."""
    lines = []
    lines.append(f"🐟 <b>{sp.scientific_name}</b>")
    if sp.author:
        year_str = f", {sp.year_described}" if sp.year_described else ""
        lines.append(f"✍️ <i>Muallif: {sp.author}{year_str}</i>")

    # Common names (UZ, EN, RU)
    if sp.common_names:
        c_names = []
        for cn in sp.common_names:
            c_names.append(f"{cn.name} ({cn.language.upper()})")
        lines.append(f"📛 <b>Xalq nomlari:</b> {', '.join(c_names[:4])}")

    # Trade names
    if getattr(sp, "trade_names", None) and sp.trade_names:
        t_names = ", ".join(tn.name for tn in sp.trade_names[:3])
        lines.append(f"🏷️ <b>Savdo nomlari:</b> {t_names}")

    # Genus / Family / Subfamily
    if sp.genus:
        fam_text = f" | Oila: <b>{sp.genus.family.scientific_name}</b>" if sp.genus.family else ""
        subfam_text = f" ({sp.genus.subfamily})" if sp.genus.subfamily else ""
        lines.append(f"🔬 Jins: <i>{sp.genus.scientific_name}</i>{subfam_text}{fam_text}")

    # Locality / Origin
    if getattr(sp, "localities", None) and sp.localities:
        loc_names = ", ".join(loc.name for loc in sp.localities[:3])
        lake_str = f" ({sp.localities[0].lake.name})" if sp.localities[0].lake else ""
        lines.append(f"🗺️ <b>Tabiiy tarqalishi:</b> {loc_names}{lake_str}")
    else:
        lines.append(f"🌍 <b>Kelib chiqishi:</b> {format_origin(sp.origin_type)}")

    # Size
    if sp.max_size_cm:
        lines.append(f"📏 <b>Maksimal o'lchami:</b> {sp.max_size_cm} sm")

    # Water summary
    if sp.temp_min is not None or sp.ph_min is not None:
        lines.append(f"💧 <b>Suv:</b> {format_range(sp.temp_min, sp.temp_max, '°C')} | pH {format_range(sp.ph_min, sp.ph_max)}")
    if sp.min_tank_liters:
        lines.append(f"🏠 <b>Tavsiya etilgan hajm:</b> {sp.min_tank_liters}+ litr")

    # Evidence badge
    badge = sp.evidence_quality_note or format_reliability(sp.reliability)
    lines.append(f"\n{badge}")
    lines.append("📚 Manbalar: <i>FishBase.org, Eschmeyer, SeriouslyFish, IUCN Red List</i>")

    return "\n".join(lines)


def format_behaviour(sp: Species) -> str:
    """Behaviour & Compatibility tab (Section F)."""
    lines = [f"🤝 <b>Xulq-atvor va muvofiqlik</b> — {sp.scientific_name}\n"]
    if sp.temperament:
        lines.append(f"🕊️ <b>Temperament:</b> {sp.temperament}")
    if sp.aggression:
        lines.append(f"⚔️ <b>Agressivlik darajasi:</b> {format_aggression(sp.aggression)}")
    if sp.conspecific_aggression:
        lines.append(f"⚡ <b>Turdoshlariga munosabat (Conspecific):</b>\n{sp.conspecific_aggression}")
    if sp.interspecific_aggression:
        lines.append(f"🛡️ <b>Boshqa turlarga munosabat (Interspecific):</b>\n{sp.interspecific_aggression}")
    if sp.group_size_recommended:
        lines.append(f"👥 <b>Tavsiya etilgan guruh tarkibi:</b> {sp.group_size_recommended}")
    if not (sp.temperament or sp.conspecific_aggression or sp.interspecific_aggression):
        lines.append(uz.NO_DATA_STRING)
    return "\n".join(lines)


def format_water_params(sp: Species) -> str:
    """Water parameters and husbandry tab (Section D)."""
    lines = [f"💧 <b>Suv parametrlari va akvarium parvarishi</b> — {sp.scientific_name}\n"]
    lines.append(f"🌡️ Harorat: {format_range(sp.temp_min, sp.temp_max, '°C')}")
    lines.append(f"💧 pH ko'rsatkichi: {format_range(sp.ph_min, sp.ph_max)}")
    lines.append(f"🧪 GH qattiqligi: {format_range(sp.gh_min, sp.gh_max)}")
    lines.append(f"🧪 KH karbonat qattiqligi: {format_range(sp.kh_min, sp.kh_max)}")

    if sp.min_tank_liters:
        lines.append(f"\n🏠 Minimal tavsiya etilgan akvarium: {sp.min_tank_liters} L")
    if sp.recommended_tank_liters:
        lines.append(f"🏠 Optimal hajm: {sp.recommended_tank_liters} L")
    if sp.tank_setup_notes:
        lines.append(f"\n🏞️ Dekoratsiyalar va dizayn: {sp.tank_setup_notes}")
    if sp.filtration_notes:
        lines.append(f"🌀 Filtratsiya: {sp.filtration_notes}")
    if sp.water_changes_notes:
        lines.append(f"🔄 Suv almashtirish: {sp.water_changes_notes}")

    return "\n".join(lines)


def format_diet(sp: Species) -> str:
    """Nutrition tab (Section E)."""
    lines = [f"🍽 <b>Oziqlanish va ratsion</b> — {sp.scientific_name}\n"]
    if sp.dietary_category:
        lines.append(f"🥗 Ozuqa toifasi: <b>{sp.dietary_category}</b>\n")
    lines.append(sp.diet_description or uz.NO_DATA_STRING)
    if sp.diet_plant:
        lines.append(f"\n🥬 O'simlikli ozuqalar: {sp.diet_plant}")
    if sp.diet_protein:
        lines.append(f"🥩 Hayvoniy oqsillar: {sp.diet_protein}")
    return "\n".join(lines)


def format_breeding(sp: Species) -> str:
    """Reproduction tab (Section G)."""
    lines = [f"🥚 <b>Ko'payish va naslchilik</b> — {sp.scientific_name}\n"]
    lines.append(f"Repromodeli: <b>{format_breeding_type(sp.breeding_type)}</b>")
    if sp.breeding_description:
        lines.append(f"\n{sp.breeding_description}")
    if sp.fry_care:
        lines.append(f"\n🐣 Chavoqlarni parvarishlash: {sp.fry_care}")
    if sp.male_description:
        lines.append(f"\n♂️ Voyaga yetgan erkak: {sp.male_description}")
    if sp.female_description:
        lines.append(f"♀️ Voyaga yetgan urg'ochi: {sp.female_description}")
    return "\n".join(lines)


def format_genetics(sp: Species) -> str:
    """Genetics and colour forms tab (Section H)."""
    lines = [f"🧬 <b>Genetika va rang shakllari</b> — {sp.scientific_name}\n"]
    if sp.genetics_info:
        lines.append(sp.genetics_info)
    if sp.color_morphs:
        lines.append(f"\n🎨 Hujjatlashtirilgan rang shakllari: {sp.color_morphs}")
    if sp.wild_form:
        lines.append(f"🌿 Tabiiy shakli (Wild form): {sp.wild_form}")
    if sp.f_generation:
        lines.append(f"🧬 Avlod belgisi: {sp.f_generation}")
    if not sp.genetics_info and not sp.color_morphs:
        lines.append(uz.NO_DATA_STRING)
    return "\n".join(lines)


def format_comparison(*species_list: Species) -> str:
    """Multi-species (2 or 3) strictly text-based comparison (Section 17)."""
    if len(species_list) < 2:
        return "Taqqoslash uchun kamida 2 ta tur tanlanishi zarur."

    lines = ["⚖️ <b>ILMIY MATNLI TAQQOSLASH (TEXT-BASED)</b>\n"]
    names = " 🆚 ".join([f"<b>{s.scientific_name}</b>" for s in species_list])
    lines.append(f"{names}\n")

    # Taxonomic status check
    sci_names = [s.scientific_name.lower() for s in species_list]
    if len(sci_names) != len(set(sci_names)):
        lines.append("ℹ️ <i>Eslatma: Tanlangan nomlar bir xil turni ifodalaydi.</i>\n")
    else:
        lines.append("🔬 <i>Taksonomik munosabat: Morfologik va tarqalish bo'yicha mustaqil alohida turlar.</i>\n")

    cols = [
        ("🧬 Oila", lambda s: s.genus.family.scientific_name if (s.genus and s.genus.family) else uz.NO_DATA_STRING),
        ("🔬 Jins", lambda s: s.genus.scientific_name if s.genus else uz.NO_DATA_STRING),
        ("✍️ Muallif/Yil", lambda s: f"{s.author or ''} {s.year_described or ''}".strip() or uz.NO_DATA_STRING),
        ("📏 Maks. o'lcham", lambda s: f"{s.max_size_cm} sm" if s.max_size_cm else uz.NO_DATA_STRING),
        ("🌡️ Harorat", lambda s: format_range(s.temp_min, s.temp_max, "°C")),
        ("💧 pH ko'rsatkich", lambda s: format_range(s.ph_min, s.ph_max)),
        ("🏠 Min. akvarium", lambda s: f"{s.min_tank_liters} L" if s.min_tank_liters else uz.NO_DATA_STRING),
        ("⚔️ Agressivlik", lambda s: format_aggression(s.aggression)),
        ("🕊️ Temperament", lambda s: s.temperament or uz.NO_DATA_STRING),
        ("🍽 Oziqlanish", lambda s: s.dietary_category or (s.diet_description[:60] + "..." if s.diet_description else uz.NO_DATA_STRING)),
        ("🥚 Ko'payish", lambda s: format_breeding_type(s.breeding_type)),
        ("🌍 Areali / Havza", lambda s: (s.localities[0].lake.name if (getattr(s, "localities", None) and s.localities and s.localities[0].lake) else format_origin(s.origin_type))),
        ("🟢 Dalil darajasi", lambda s: s.evidence_quality_note or format_reliability(s.reliability)),
    ]

    for label, extractor in cols:
        lines.append(f"<b>{label}:</b>")
        for s in species_list:
            lines.append(f"  ▫️ <i>{s.scientific_name}</i>: {extractor(s)}")
        lines.append("")

    return "\n".join(lines)


async def safe_answer_html(message, text: str, reply_markup=None):
    """Safely answer message with HTML, automatically falling back to clean text on parsing errors."""
    import re
    if len(text) > 4000:
        text = text[:3990] + "..."
    try:
        return await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        err_str = str(e).lower()
        if "can't parse entities" in err_str or "entity" in err_str:
            clean_text = re.sub(r"<[^>]+>", "", text)
            return await message.answer(clean_text, reply_markup=reply_markup, parse_mode=None)
        raise
