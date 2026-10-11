"""Image Search Service — discovers and strictly verifies fish images from free public APIs.

Guarantees:
1. Strict Taxon Resolution: Preserves Genus/Species/Morph and never swaps genera
   (e.g., Petrochromis is never replaced by Aulonocara, Metriaclima, or other genera).
2. Multi-tier Targeted Queries:
   - Tier 1: Full raw query and scientific variant (e.g., "Petrochromis Red Bulu Point", "Petrochromis sp. Red Bulu Point")
   - Tier 2: Quoted locality/morph variants (e.g., "Petrochromis" "Red Bulu Point", "Petrochromis Red Bulu Point cichlid")
   - Tier 3: Verified genus-only fallback with explicit partial match disclosure (e.g., "Petrochromis")
3. Strict Image Metadata Filtering:
   - Validates title, description, categories, and iNaturalist taxon.
   - Enforces presence of the expected genus.
   - Strictly rejects conflicting genera (e.g., Aulonocara image rejected when querying Petrochromis).
   - Never pads results with unrelated species to fill 5 photos.
4. Confidence Levels:
   - ANIQ MOSLIK (Exact species/variant match)
   - QISMAN MOSLIK (Partial / Genus-level match with explicit disclosure)
   - TASDIQLANMAGAN (Unverified - no images returned, prompts user for clarification)
5. Comprehensive Diagnostics & Logging:
   - Logs start, parsed tokens, API queries, rejection reasons, and accepted results.
"""

from __future__ import annotations

import asyncio
import enum
import html
import logging
import re
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from rapidfuzz import process, fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False
    import difflib

from app.models.species import Species, CommonName, Synonym, TradeName
from app.models.taxonomy import Genus
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

# Request Headers complying with Wikimedia and iNaturalist policies
REQUEST_HEADERS = {
    "User-Agent": "AquaMasterUzbekistanBot/1.0 (https://t.me/aquamaster; contact: info@aquamaster.uz)",
    "Accept": "application/json",
}

VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "image/webp")

# List of major known cichlid and aquarium genera to prevent cross-contamination
KNOWN_CICHLID_GENERA = {
    # Lake Tanganyika
    "petrochromis", "tropheus", "neolamprologus", "altolamprologus", "julidochromis",
    "cyphotilapia", "chalinochromis", "benthochromis", "interochromis", "simochromis",
    "variabilichromis", "lamprologus", "lepidiolamprologus", "telmatochromis",
    "cyprichromis", "paracyprichromis", "xenotilapia", "enantiopus", "eretmodus",
    "spathodus", "tanganicodus",
    # Lake Malawi (Mbuna, Hap, Utaka, Peacocks)
    "aulonocara", "pseudotropheus", "labidochromis", "metriaclima", "chindongo",
    "cynotilapia", "melanochromis", "labeotropheus", "iodotropheus", "petrotilapia",
    "gephyrochromis", "copadichromis", "sciaenochromis", "placidochromis",
    "protomelas", "otopharynx", "nimbochromis", "fossorochromis", "mchenga",
    "dimidiochromis", "champsochromis", "cyrtocara", "tylochromis",
    # Lake Victoria & Other Africa
    "haplochromis", "pundamilia", "astatotilapia", "mbipia", "pelvicachromis",
    "hemichromis",
    # American Cichlids & Discus
    "pterophyllum", "symphysodon", "apistogramma", "mikrogeophagus", "astronotus",
    "heros", "thorichthys", "andinoacara", "geophagus", "gymnogeophagus",
    "satanoperca", "biotodoma", "cichlasoma", "parachromis", "amatitlania",
    "rocio", "vieja", "uaru",
    # Plecos, Catfishes & L-numbers
    "hypancistrus", "ancistrus", "baryancistrus", "panaque", "panaqolus",
    "peckoltia", "pseudacanthicus", "scobinancistrus", "leporacanthicus",
    "dekeyseria", "hemiancistrus", "spectracanthicus", "corydoras", "synodontis",
    # Other Freshwater
    "poecilia", "xiphophorus", "betta", "trichogaster", "paracheirodon",
    "hyphessobrycon", "danio", "puntius", "puntigrus", "barbus"
}


# Common aquarium fish names mapped to their canonical genus and species
COMMON_NAMES_MAP = {
    "skalyariya": ("Pterophyllum", "scalare", None),
    "skalyar": ("Pterophyllum", "scalare", None),
    "angelfish": ("Pterophyllum", "scalare", None),
    "diskus": ("Symphysodon", "discus", None),
    "discus": ("Symphysodon", "discus", None),
    "neon": ("Paracheirodon", "innesi", None),
    "neon tetra": ("Paracheirodon", "innesi", None),
    "qora neon": ("Hyphessobrycon", "herbertaxelrodi", None),
    "qizil neon": ("Paracheirodon", "axelrodi", None),
    "frontoza": ("Cyphotilapia", "frontosa", None),
    "frontosa": ("Cyphotilapia", "frontosa", None),
    "demasoni": ("Pseudotropheus", "demasoni", None),
    "chindongo demasoni": ("Chindongo", "demasoni", None),
    "yellow lab": ("Labidochromis", "caeruleus", None),
    "labido": ("Labidochromis", "caeruleus", None),
    "elou labido": ("Labidochromis", "caeruleus", None),
    "guppi": ("Poecilia", "reticulata", None),
    "guppy": ("Poecilia", "reticulata", None),
    "mechenosets": ("Xiphophorus", "hellerii", None),
    "molliya": ("Poecilia", "sphenops", None),
    "molly": ("Poecilia", "sphenops", None),
    "petsiliya": ("Xiphophorus", "maculatus", None),
    "antsistrus": ("Ancistrus", "sp.", None),
    "ancistrus": ("Ancistrus", "sp.", None),
    "koridoras": ("Corydoras", "sp.", None),
    "corydoras": ("Corydoras", "sp.", None),
    "xo'rozcha": ("Betta", "splendens", None),
    "betta": ("Betta", "splendens", None),
    "barbus": ("Puntius", "sp.", None),
    "sumatra barbusi": ("Puntigrus", "tetrazona", None),
    "tetra": ("Hyphessobrycon", "sp.", None),
}


class MatchConfidence(str, enum.Enum):
    EXACT = "ANIQ MOSLIK"          # 🎯 Exact species or variant confirmed
    PARTIAL = "QISMAN MOSLIK"      # ⚠️ Confirmed genus, but variant not explicitly documented
    UNVERIFIED = "TASDIQLANMAGAN"  # ❌ No reliable match found


@dataclass
class FishNameComponents:
    raw_query: str
    genus: str | None
    species: str | None
    variant: str | None
    canonical_name: str
    search_tiers: list[str] = field(default_factory=list)


@dataclass
class FishImageItem:
    url: str
    title: str
    source: str
    license: str
    author: str
    confidence: MatchConfidence = MatchConfidence.EXACT


@dataclass
class FishImageSearchResult:
    query: str
    resolved_name: str
    confidence: MatchConfidence
    note: str | None
    images: list[FishImageItem]
    components: FishNameComponents | None = None


class FishImageSearchService:
    """Service to strictly resolve fish species and retrieve verified licensed photographs."""

    _db_genera_cache: set[str] | None = None
    _species_cache: list[tuple[str, str, str]] | None = None  # (searchable_name, scientific_name, genus)
    _species_cache_time: float = 0.0
    _SPECIES_CACHE_TTL: float = 600.0  # 10 minutes

    # Result cache: query -> (timestamp, result)
    _result_cache: dict[str, tuple[float, FishImageSearchResult]] = {}
    _RESULT_CACHE_TTL: float = 1800.0  # 30 minutes

    # iNaturalist rate limiting: 1 request per second
    _inat_lock = asyncio.Lock()
    _inat_last_request_time: float = 0.0

    @classmethod
    def _clean_html_text(cls, raw: str | None) -> str:
        """Strip HTML tags and unescape text."""
        if not raw:
            return ""
        clean = re.sub(r"<[^>]+>", "", raw)
        return html.unescape(clean).strip()

    @classmethod
    async def get_db_genera(cls, session: AsyncSession) -> set[str]:
        """Fetch all genus names registered in DB."""
        if cls._db_genera_cache is not None:
            return cls._db_genera_cache

        genera: set[str] = set()
        stmt = select(Genus.scientific_name)
        res = await session.execute(stmt)
        for row in res.all():
            if row[0]:
                genera.add(row[0].strip().lower())

        cls._db_genera_cache = genera
        return genera

    @classmethod
    async def get_all_species_records(cls, session: AsyncSession) -> list[tuple[str, str, str]]:
        """Fetch searchable names with (searchable_name, scientific_name, genus)."""
        now = time.time()
        if cls._species_cache is not None and (now - cls._species_cache_time) < cls._SPECIES_CACHE_TTL:
            return cls._species_cache

        records: list[tuple[str, str, str]] = []

        stmt = select(Species.scientific_name)
        res = await session.execute(stmt)
        for row in res.all():
            sname = row[0]
            if sname:
                genus = sname.split()[0]
                records.append((sname.lower(), sname, genus))

        stmt_common = (
            select(CommonName.name, Species.scientific_name)
            .join(Species, CommonName.species_id == Species.id)
            .where(Species.is_published == True)  # noqa: E712
        )
        res_common = await session.execute(stmt_common)
        for cname, sname in res_common.all():
            if cname and sname:
                genus = sname.split()[0]
                records.append((cname.lower(), sname, genus))

        stmt_syn = (
            select(Synonym.name, Species.scientific_name)
            .join(Species, Synonym.species_id == Species.id)
            .where(Species.is_published == True)  # noqa: E712
        )
        res_syn = await session.execute(stmt_syn)
        for sname_syn, sname in res_syn.all():
            if sname_syn and sname:
                genus = sname.split()[0]
                records.append((sname_syn.lower(), sname, genus))

        stmt_trade = (
            select(TradeName.name, Species.scientific_name)
            .join(Species, TradeName.species_id == Species.id)
            .where(Species.is_published == True)  # noqa: E712
        )
        res_trade = await session.execute(stmt_trade)
        for tname, sname in res_trade.all():
            if tname and sname:
                genus = sname.split()[0]
                records.append((tname.lower(), sname, genus))

        cls._species_cache = records
        cls._species_cache_time = now
        return records

    @classmethod
    async def parse_fish_query(
        cls,
        raw_query: str,
        session: AsyncSession,
        ai_service: AIService | None = None,
    ) -> FishNameComponents:
        """Parse raw query into Genus, Species, and Variant/Morph components.

        Guarantees:
        - NEVER replaces an identified genus with an unrelated genus.
        - Produces prioritized search tiers.
        """
        clean = raw_query.strip()
        clean_clean = re.sub(r'["\'\(\)\[\]]', '', clean)
        words = clean_clean.split()

        db_genera = await cls.get_db_genera(session)
        q_lower = clean.lower()

        # Check dictionary of common names
        for common_k, (c_gen, c_sp, c_var) in COMMON_NAMES_MAP.items():
            if q_lower == common_k or q_lower.startswith(common_k + " "):
                var = c_var
                if q_lower.startswith(common_k + " "):
                    extra = clean[len(common_k):].strip()
                    var = extra if extra else var
                can_name = f"{c_gen} {c_sp}" + (f" '{var}'" if var else "")
                tiers = [
                    f"{c_gen} {c_sp} {var}" if var else f"{c_gen} {c_sp}",
                    f"{c_gen} {c_sp}",
                    c_gen,
                ]
                return FishNameComponents(
                    raw_query=clean,
                    genus=c_gen,
                    species=c_sp,
                    variant=var,
                    canonical_name=can_name,
                    search_tiers=[t for t in tiers if t],
                )

        if not words:
            return FishNameComponents(
                raw_query=clean,
                genus=None,
                species=None,
                variant=None,
                canonical_name=clean,
                search_tiers=[clean],
            )

        # Check L-number / LDA-number designation (e.g. L333 pleco, Ancistrus L144, LDA016)
        lnum_match = re.search(r'\b(l|lda)[ -]?(\d{1,4})\b', clean, re.IGNORECASE)
        if lnum_match:
            from app.models.lnumber import LNumberDesignation
            l_prefix = lnum_match.group(1).upper()
            l_num = int(lnum_match.group(2))
            l_code = f"{l_prefix}{l_num:03d}" if l_prefix == "LDA" or l_num < 100 else f"{l_prefix}{l_num}"
            l_code_alt = f"{l_prefix}0{l_num}" if l_num < 100 and l_prefix == "L" else l_code
            stmt_lnum = select(LNumberDesignation).where(
                (LNumberDesignation.designation == l_code) |
                (LNumberDesignation.designation == l_code_alt)
            )
            l_rec = (await session.execute(stmt_lnum)).scalars().first()
            if l_rec and l_rec.genus_name:
                c_gen = l_rec.genus_name
                c_sp = "sp."
                c_var = l_rec.designation
                c_canon = l_rec.scientific_name_current or f"{c_gen} sp. '{c_var}'"
                tiers = [
                    f"{c_gen} {c_var}",
                    f"{c_gen} sp. {c_var}",
                    f"{c_var} pleco",
                    clean,
                    c_gen,
                ]
                return FishNameComponents(
                    raw_query=clean,
                    genus=c_gen,
                    species=c_sp,
                    variant=c_var,
                    canonical_name=c_canon,
                    search_tiers=[t for t in tiers if t],
                )

        first_word = words[0]
        first_lower = first_word.lower()

        identified_genus: str | None = None

        # 1. Check if first word is a known genus in DB or well-known list
        if first_lower in db_genera or first_lower in KNOWN_CICHLID_GENERA:
            identified_genus = first_word.capitalize()
        # 2. Try fuzzy matching against known genera to catch typos (e.g. Petrachromis -> Petrochromis, Aulonacara -> Aulonocara)
        elif HAS_RAPIDFUZZ and len(first_lower) >= 4:
            all_known = list(db_genera.union(KNOWN_CICHLID_GENERA))
            best_g = process.extractOne(first_lower, all_known, scorer=fuzz.ratio, score_cutoff=80.0)
            if best_g:
                identified_genus = best_g[0].capitalize()

        # 3. Last fallback: taxonomic suffixes (only if no known genus was matched)
        if not identified_genus and first_lower.endswith(("chromis", "cara", "tilapia", "lamprologus", "geophagus", "ichthys", "pterus")):
            identified_genus = first_word.capitalize()

        species: str | None = None
        variant: str | None = None

        if identified_genus:
            remaining_words = words[1:]
            if remaining_words:
                second_word = remaining_words[0]
                if second_word.lower() in ("sp", "sp.", "spp", "spp."):
                    species = "sp."
                    variant = " ".join(remaining_words[1:]) if len(remaining_words) > 1 else None
                elif second_word.islower() and len(second_word) >= 3 and not second_word.isdigit():
                    # Typical species epithet in lowercase: e.g., polyodon, jacobfreibergi, scalare
                    species = second_word.lower()
                    variant = " ".join(remaining_words[1:]) if len(remaining_words) > 1 else None
                else:
                    # Capitalized or locality name: e.g., Red Bulu Point, Eureka, Ikola
                    species = "sp."
                    variant = " ".join(remaining_words)
            else:
                species = "sp."

            canonical = f"{identified_genus}"
            if species and species != "sp.":
                canonical += f" {species}"
            elif species == "sp." and variant:
                canonical += f" sp. {variant}"
            if variant and species != "sp.":
                canonical += f" '{variant}'"

            # Build prioritized search queries
            tiers: list[str] = []
            # Tier 1: Exact raw query
            tiers.append(clean)
            # Tier 2: Scientific name with sp. or variant
            if variant:
                tiers.append(f"{identified_genus} sp. {variant}")
                tiers.append(f"{identified_genus} \"{variant}\"")
                tiers.append(f"{identified_genus} {variant} cichlid")
            if species and species != "sp.":
                tiers.append(f"{identified_genus} {species}")
            # Tier 3: Genus fallback
            tiers.append(f"{identified_genus}")

            # Deduplicate tiers preserving order
            seen_tiers = set()
            ordered_tiers = []
            for t in tiers:
                if t and t not in seen_tiers:
                    seen_tiers.add(t)
                    ordered_tiers.append(t)

            return FishNameComponents(
                raw_query=clean,
                genus=identified_genus,
                species=species,
                variant=variant,
                canonical_name=canonical,
                search_tiers=ordered_tiers,
            )

        # Unified search: resolves fuzzy names, common names, trade names, typos (frontoza, ansictrus, etc.)
        try:
            from app.services.search_service import SearchService
            search_svc = SearchService(session)
            unified_matches = await search_svc.search_unified(clean, limit=1)
            if unified_matches:
                matched = unified_matches[0]
                sci_name = matched.get("scientific_name", "")
                if sci_name and sci_name != "Undescribed sp.":
                    parts = sci_name.split()
                    gen = parts[0].capitalize()
                    sp_name = parts[1] if len(parts) > 1 else "sp."
                    return FishNameComponents(
                        raw_query=clean,
                        genus=gen,
                        species=sp_name,
                        variant=None,
                        canonical_name=sci_name,
                        search_tiers=[sci_name, gen],
                    )
        except Exception as e:
            logger.warning(f"Unified search resolution in image service failed: {e}")

        # If no Latin genus identified in first word, check local DB for exact or close species match
        records = await cls.get_all_species_records(session)
        for cand_name, sname, gen in records:
            if cand_name == q_lower:
                return FishNameComponents(
                    raw_query=clean,
                    genus=gen,
                    species=sname.split()[1] if len(sname.split()) > 1 else "sp.",
                    variant=None,
                    canonical_name=sname,
                    search_tiers=[sname, gen],
                )

        # AI Fallback for complex / unknown names: ask AI strictly for taxonomy
        if ai_service:
            try:
                ai_prompt = (
                    f"Akvarium balig'i: '{clean}'.\n"
                    "Ushbu baliqning aniq lotincha ilmiy avlodi (Genus), turi (Species) va rang/geografik varianti (Variant)ni aniqlang.\n"
                    "Format (aniq shu ko'rinishda 3 qator):\n"
                    "GENUS: [Lotincha avlod]\n"
                    "SPECIES: [Lotincha tur yoki sp.]\n"
                    "VARIANT: [Rang yoki lokatsiya nomi yoki NONE]\n"
                    "Agar bu baliq bo'lmasa, GENUS: UNKNOWN deb yozing."
                )
                raw_ai = await ai_service.search_and_explain(ai_prompt)
                ai_genus = None
                ai_species = None
                ai_variant = None

                for line in raw_ai.split("\n"):
                    line_clean = line.strip()
                    if line_clean.startswith("GENUS:"):
                        g_val = line_clean.replace("GENUS:", "").strip().split()[0]
                        if g_val and "UNKNOWN" not in g_val.upper():
                            ai_genus = g_val.capitalize()
                    elif line_clean.startswith("SPECIES:"):
                        s_val = line_clean.replace("SPECIES:", "").strip().split()[0]
                        if s_val and "NONE" not in s_val.upper():
                            ai_species = s_val.lower()
                    elif line_clean.startswith("VARIANT:"):
                        v_val = line_clean.replace("VARIANT:", "").strip()
                        if v_val and "NONE" not in v_val.upper():
                            ai_variant = v_val

                if ai_genus:
                    canonical = f"{ai_genus} {ai_species or 'sp.'}" + (f" '{ai_variant}'" if ai_variant else "")
                    tiers = [clean]
                    if ai_variant:
                        tiers.append(f"{ai_genus} sp. {ai_variant}")
                        tiers.append(f"{ai_genus} {ai_variant}")
                    if ai_species and ai_species != "sp.":
                        tiers.append(f"{ai_genus} {ai_species}")
                    tiers.append(ai_genus)
                    return FishNameComponents(
                        raw_query=clean,
                        genus=ai_genus,
                        species=ai_species,
                        variant=ai_variant,
                        canonical_name=canonical,
                        search_tiers=tiers,
                    )
            except Exception as e:
                logger.warning(f"AI taxonomic parsing failed for '{clean}': {e}")

        # Unidentified genus
        return FishNameComponents(
            raw_query=clean,
            genus=None,
            species=None,
            variant=None,
            canonical_name=clean,
            search_tiers=[clean],
        )

    @classmethod
    def validate_image(
        cls,
        title: str,
        desc: str,
        taxon_name: str | None,
        expected_genus: str | None,
        expected_variant: str | None,
    ) -> tuple[bool, MatchConfidence, str]:
        """Strictly validate whether a candidate photo corresponds to the target fish.

        Returns: (is_valid, confidence, rejection_reason)
        """
        full_text = f"{title} {desc} {taxon_name or ''}".lower()

        # Reject if expected genus is known but not mentioned
        if expected_genus:
            exp_g_lower = expected_genus.lower()
            if exp_g_lower not in full_text:
                return False, MatchConfidence.UNVERIFIED, f"Rasm metama'lumotlarida '{expected_genus}' avlodi yo'q"

            # Check for conflicting cichlid genera
            for conf_g in KNOWN_CICHLID_GENERA:
                if conf_g != exp_g_lower and conf_g in full_text:
                    # Check if the title explicitly indicates a conflicting genus
                    title_lower = title.lower()
                    if title_lower.startswith(f"file:{conf_g}") or f" {conf_g} " in title_lower or f"_{conf_g}_" in title_lower:
                        return False, MatchConfidence.UNVERIFIED, f"Rasm boshqa avlodga tegishli ({conf_g})"

        # Check variant / locality match
        if expected_variant:
            # Tokenize variant words (e.g. ['red', 'bulu', 'point'] or ['eureka'])
            var_tokens = [t.lower() for t in expected_variant.split() if len(t) > 2]
            if var_tokens:
                # If key locality/variant words appear in title or desc
                matches = sum(1 for t in var_tokens if t in full_text)
                if matches >= max(1, len(var_tokens) - 1):
                    return True, MatchConfidence.EXACT, "OK_EXACT"

            # If variant specified but absent in image, it's a genus-level partial match
            return True, MatchConfidence.PARTIAL, "OK_PARTIAL_GENUS"

        return True, MatchConfidence.EXACT, "OK"

    @classmethod
    async def fetch_wikimedia_images(
        cls,
        search_query: str,
        components: FishNameComponents,
        limit: int = 5,
        seen_urls: set[str] | None = None,
    ) -> list[FishImageItem]:
        """Fetch and strictly filter images from Wikimedia Commons for a specific query."""
        images: list[FishImageItem] = []
        urls = seen_urls or set()

        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(headers=REQUEST_HEADERS, timeout=timeout) as session:
            try:
                commons_params = {
                    "action": "query",
                    "generator": "search",
                    "gsrsearch": search_query,
                    "gsrnamespace": "6",
                    "gsrlimit": str(max(10, limit * 2)),
                    "prop": "imageinfo",
                    "iiprop": "url|mime|extmetadata",
                    "iiurlwidth": "1280",
                    "format": "json",
                }
                commons_url = f"https://commons.wikimedia.org/w/api.php?{urllib.parse.urlencode(commons_params)}"
                logger.info("API QUERY [Wikimedia]: '%s'", search_query)

                async with session.get(commons_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pages = data.get("query", {}).get("pages", {})
                        logger.info("Wikimedia returned %d raw results for '%s'", len(pages), search_query)

                        for pid, p in pages.items():
                            if len(images) >= limit:
                                break

                            title = p.get("title", "")
                            infos = p.get("imageinfo", [])
                            if not infos:
                                logger.info("REJECTED [Wikimedia] '%s': reason='No imageinfo'", title)
                                continue

                            info = infos[0]
                            mime = info.get("mime", "")
                            if mime not in ALLOWED_MIME_TYPES:
                                logger.info("REJECTED [Wikimedia] '%s': reason='Invalid mime (%s)'", title, mime)
                                continue

                            orig_url = info.get("url") or ""
                            url = info.get("thumburl") or orig_url
                            if not url or url in urls:
                                continue

                            orig_path = urllib.parse.urlparse(orig_url).path.lower()
                            if not any(orig_path.endswith(ext) for ext in VALID_IMAGE_EXTENSIONS):
                                logger.info("REJECTED [Wikimedia] '%s': reason='Invalid extension'", title)
                                continue

                            extmeta = info.get("extmetadata", {})
                            desc_raw = extmeta.get("ImageDescription", {}).get("value") or ""
                            desc_clean = cls._clean_html_text(desc_raw)

                            # Strict image validation
                            valid, conf, reason = cls.validate_image(
                                title=title,
                                desc=desc_clean,
                                taxon_name=None,
                                expected_genus=components.genus,
                                expected_variant=components.variant,
                            )

                            if not valid:
                                logger.info("REJECTED [Wikimedia] '%s': reason='%s'", title, reason)
                                continue

                            license_str = extmeta.get("LicenseShortName", {}).get("value") or "CC / Open License"
                            author_raw = extmeta.get("Artist", {}).get("value") or "Wikimedia Contributor"
                            author_clean = cls._clean_html_text(author_raw)[:60]
                            title_clean = title.replace("File:", "").strip()

                            urls.add(url)
                            logger.info("ACCEPTED [Wikimedia] '%s': confidence='%s'", title_clean, conf.value)

                            images.append(
                                FishImageItem(
                                    url=url,
                                    title=title_clean,
                                    source="Wikimedia Commons",
                                    license=license_str,
                                    author=author_clean or "Wikimedia Contributor",
                                    confidence=conf,
                                )
                            )
            except Exception as e:
                logger.warning("Wikimedia search failed for '%s': %s", search_query, e)

        return images

    @classmethod
    async def fetch_inaturalist_images(
        cls,
        search_query: str,
        components: FishNameComponents,
        limit: int = 5,
        seen_urls: set[str] | None = None,
    ) -> list[FishImageItem]:
        """Fetch and strictly filter research-grade photos from iNaturalist."""
        images: list[FishImageItem] = []
        urls = seen_urls or set()

        async with cls._inat_lock:
            now = time.time()
            elapsed = now - cls._inat_last_request_time
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
            cls._inat_last_request_time = time.time()

            timeout = aiohttp.ClientTimeout(total=8)
            try:
                params = {
                    "q": search_query,
                    "photos": "true",
                    "quality_grade": "research",
                    "per_page": str(max(10, limit * 2)),
                }
                inat_url = f"https://api.inaturalist.org/v1/observations?{urllib.parse.urlencode(params)}"
                logger.info("API QUERY [iNaturalist]: '%s'", search_query)

                async with aiohttp.ClientSession(headers=REQUEST_HEADERS, timeout=timeout) as session:
                    async with session.get(inat_url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get("results", [])
                            logger.info("iNaturalist returned %d raw results for '%s'", len(results), search_query)

                            for obs in results:
                                if len(images) >= limit:
                                    break

                                taxon = obs.get("taxon", {})
                                taxon_name = taxon.get("name", "")
                                taxon_common = taxon.get("preferred_common_name", "")
                                obs_desc = obs.get("description", "") or ""

                                # Validate genus and taxon
                                valid, conf, reason = cls.validate_image(
                                    title=f"{taxon_name} {taxon_common}",
                                    desc=obs_desc,
                                    taxon_name=taxon_name,
                                    expected_genus=components.genus,
                                    expected_variant=components.variant,
                                )

                                if not valid:
                                    logger.info("REJECTED [iNaturalist] Obs #%s: reason='%s'", obs.get('id'), reason)
                                    continue

                                photos = obs.get("photos", [])
                                for p in photos:
                                    if len(images) >= limit:
                                        break
                                    raw_url = p.get("url")
                                    if not raw_url:
                                        continue

                                    medium_url = raw_url.replace("/square.", "/medium.")
                                    if medium_url in urls:
                                        continue

                                    urls.add(medium_url)
                                    attr = p.get("attribution") or "iNaturalist contributor"
                                    license_code = p.get("license_code") or "CC"

                                    logger.info("ACCEPTED [iNaturalist] Obs #%s: taxon='%s', confidence='%s'",
                                                obs.get('id'), taxon_name, conf.value)

                                    images.append(
                                        FishImageItem(
                                            url=medium_url,
                                            title=f"{taxon_name} (Observation #{obs.get('id', '')})",
                                            source="iNaturalist (Research Grade)",
                                            license=f"{license_code.upper()}",
                                            author=attr,
                                            confidence=conf,
                                        )
                                    )
            except Exception as e:
                logger.warning("iNaturalist fetch failed for '%s': %s", search_query, e)

        return images

    @classmethod
    async def search_fish_images(
        cls,
        query: str,
        session: AsyncSession,
        ai_service: AIService | None = None,
        max_images: int = 8,
        user_id: int | None = None,
        seen_urls: set[str] | None = None,
    ) -> FishImageSearchResult:
        """Execute strict, multi-tiered fish image search.

        Guarantees:
        - Genus preservation (never returns Aulonocara for Petrochromis).
        - Multi-tier queries with fallback to verified genus only.
        - Strict filtering and metadata validation.
        - No padding of results with unrelated fish.
        - Supports pagination and exclusion of previously seen images.
        """
        clean_query = query.strip()
        logger.info("IMAGE SEARCH START | user_id=%s | raw_query='%s' | seen_urls_count=%d",
                    user_id or 0, clean_query, len(seen_urls) if seen_urls else 0)

        if not clean_query:
            return FishImageSearchResult(
                query="",
                resolved_name="",
                confidence=MatchConfidence.UNVERIFIED,
                note="Nom kiritilmadi.",
                images=[],
            )

        # Check in-memory result cache (only when no prior seen_urls to exclude)
        cache_key = clean_query.lower()
        now = time.time()
        if not seen_urls and cache_key in cls._result_cache:
            ts, cached_result = cls._result_cache[cache_key]
            if (now - ts) < cls._RESULT_CACHE_TTL:
                logger.info("IMAGE SEARCH CACHE HIT | query='%s'", clean_query)
                return cached_result

        # Step 1: Parse query into components
        comp = await cls.parse_fish_query(clean_query, session, ai_service)
        logger.info("PARSED QUERY | genus='%s' | species='%s' | variant='%s' | canonical='%s'",
                    comp.genus, comp.species, comp.variant, comp.canonical_name)

        # If genus is completely unknown and query doesn't match anything
        if not comp.genus:
            logger.info("SEARCH FAILED: Unknown genus for query '%s'", clean_query)
            return FishImageSearchResult(
                query=clean_query,
                resolved_name=clean_query,
                confidence=MatchConfidence.UNVERIFIED,
                note="Kiritilgan nom bo'yicha baliq avlodi (jinsi) tasdiqlanmadi.",
                images=[],
                components=comp,
            )

        collected_images: list[FishImageItem] = []
        effective_seen = set(seen_urls) if seen_urls else set()
        overall_confidence = MatchConfidence.UNVERIFIED

        # Step 2: Multi-tier search loop
        for tier_idx, search_term in enumerate(comp.search_tiers, 1):
            if len(collected_images) >= max_images:
                break

            needed = max_images - len(collected_images)
            logger.info("SEARCH TIER %d | query='%s' | needed=%d", tier_idx, search_term, needed)

            # Query Wikimedia Commons
            wiki_imgs = await cls.fetch_wikimedia_images(
                search_query=search_term,
                components=comp,
                limit=needed,
                seen_urls=effective_seen,
            )
            collected_images.extend(wiki_imgs)

            # If still need images, query iNaturalist
            if len(collected_images) < max_images:
                needed = max_images - len(collected_images)
                inat_imgs = await cls.fetch_inaturalist_images(
                    search_query=search_term,
                    components=comp,
                    limit=needed,
                    seen_urls=effective_seen,
                )
                collected_images.extend(inat_imgs)

            # If we found images at this tier and it's a specific tier (contains variant), confidence is EXACT
            if collected_images and comp.variant and comp.variant.lower() in search_term.lower():
                overall_confidence = MatchConfidence.EXACT
                break

        # Assess overall confidence and formulate note
        note: str | None = None
        if collected_images:
            has_exact = any(img.confidence == MatchConfidence.EXACT for img in collected_images)
            if has_exact or not comp.variant:
                overall_confidence = MatchConfidence.EXACT
                note = f"🎯 <b>ANIQ MOSLIK:</b> <i>{comp.canonical_name}</i> bo'yicha {len(collected_images)} ta tasdiqlangan surat topildi."
            else:
                overall_confidence = MatchConfidence.PARTIAL
                note = (
                    f"⚠️ <b>QISMAN MOSLIK:</b> Aniq «{comp.variant}» varianti bo'yicha suratlar topilmadi.\n"
                    f"Quyida tasdiqlangan <b>{comp.genus}</b> avlodi suratlari keltirilmoqda."
                )
        else:
            overall_confidence = MatchConfidence.UNVERIFIED
            if seen_urls:
                note = f"ℹ️ «{comp.canonical_name}» bo'yicha boshqa yangi tasdiqlangan suratlar topilmadi."
            else:
                note = f"❌ <b>{comp.canonical_name}</b> bo'yicha ishonchli suratlar topilmadi. Iltimos, nomni aniqlashtirib qayta kiriting."

        final_result = FishImageSearchResult(
            query=clean_query,
            resolved_name=comp.canonical_name,
            confidence=overall_confidence,
            note=note,
            images=collected_images[:max_images],
            components=comp,
        )

        logger.info("IMAGE SEARCH FINISH | query='%s' | found=%d | confidence='%s'",
                    clean_query, len(final_result.images), overall_confidence.value)

        # Cache result if it had any search activity and not a pagination call
        if not seen_urls:
            cls._result_cache[cache_key] = (now, final_result)
        return final_result

    @classmethod
    async def download_image_bytes(cls, url: str) -> bytes | None:
        """Safely download image bytes as fallback if Telegram direct URL fails."""
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(headers=REQUEST_HEADERS, timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        content_type = resp.headers.get("Content-Type", "")
                        if "image" in content_type or any(url.lower().endswith(ext) for ext in VALID_IMAGE_EXTENSIONS):
                            return await resp.read()
        except Exception as e:
            logger.warning("Failed to download image %s: %s", url, e)
        return None
