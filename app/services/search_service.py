"""Search service with multi-tier exact, token, and fuzzy matching."""

from __future__ import annotations

import re
from typing import Any
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

from app.models.species import Species, CommonName, Synonym, TradeName
from app.models.taxonomy import Genus, Family
from app.models.locality import Locality, Lake
from app.models.lnumber import LNumberDesignation
from app.repositories import SpeciesRepository, LNumberRepository
from app.utils.validators import sanitize_search_query


class SearchService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.species_repo = SpeciesRepository(session)
        self.lnumber_repo = LNumberRepository(session)

    async def search(self, query: str, limit: int = 20) -> list[Species]:
        """Search species using exact, token, and fuzzy matching (returns Species objects)."""
        clean = sanitize_search_query(query).strip()
        if len(clean) < 2:
            return []

        # 1. Direct search through repository
        results = await self.species_repo.search(clean, limit=limit)
        if results:
            for sp in results:
                await self.species_repo.increment_search_count(sp.id)
            return results

        # 2. Token-based fallback if multiple words
        tokens = [t for t in re.split(r"[\s\-_]+", clean) if len(t) >= 3]
        if len(tokens) > 1:
            for token in tokens:
                token_results = await self.species_repo.search(token, limit=limit)
                if token_results:
                    for sp in token_results:
                        await self.species_repo.increment_search_count(sp.id)
                    return token_results

        # 3. Fuzzy match fallback with rapidfuzz (typos like 'frontoza', 'ansictrus')
        if HAS_RAPIDFUZZ:
            fuzzy_results = await self._fuzzy_search_species(clean, limit=limit)
            if fuzzy_results:
                for sp in fuzzy_results:
                    await self.species_repo.increment_search_count(sp.id)
                return fuzzy_results

        return []

    async def search_lnumbers(self, query: str, limit: int = 15) -> list[LNumberDesignation]:
        """Search L-numbers by code, current scientific name, or trade name."""
        clean = sanitize_search_query(query).strip()
        if len(clean) < 2:
            return []

        # Extract L/LDA designation pattern if present (e.g. L144, L-144, LDA016)
        l_match = re.search(r"\b(L|LDA)\s*[-_]?\s*(\d+)\b", clean, re.IGNORECASE)
        if l_match:
            prefix = l_match.group(1).upper()
            num = l_match.group(2)
            # Try plain prefix+num and prefix+zero-padded
            for des in [f"{prefix}{num}", f"{prefix}{num.zfill(3)}"]:
                exact = await self.lnumber_repo.get_by_designation(des)
                if exact:
                    return [exact]

        exact = await self.lnumber_repo.get_by_designation(clean)
        if exact:
            return [exact]

        results = await self.lnumber_repo.search(clean, limit=limit)
        if results:
            return results

        # Fuzzy search across L-numbers
        if HAS_RAPIDFUZZ:
            stmt = select(LNumberDesignation)
            res = await self.session.execute(stmt)
            all_lnums = list(res.scalars().all())

            scored = []
            q_lower = clean.lower()
            for item in all_lnums:
                targets = [
                    item.designation.lower(),
                    (item.scientific_name_current or "").lower(),
                    (item.common_name_uz or "").lower(),
                    (item.common_name_en or "").lower(),
                    (item.trade_names or "").lower(),
                ]
                best_score = max(fuzz.WRatio(q_lower, t) for t in targets if t)
                if best_score >= 65:
                    scored.append((best_score, item))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [item for _, item in scored[:limit]]

        return []

    async def search_unified(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Unified search across Species and L-numbers with relevance ranking."""
        clean = sanitize_search_query(query).strip()
        if len(clean) < 2:
            return []

        results: list[dict[str, Any]] = []
        seen_species_ids = set()
        seen_lnum_ids = set()

        # 1. Check L-number designation explicitly
        lnum_matches = await self.search_lnumbers(clean, limit=5)
        for item in lnum_matches:
            if item.id not in seen_lnum_ids:
                seen_lnum_ids.add(item.id)
                sci = item.scientific_name_current or "Undescribed sp."
                results.append({
                    "type": "lnumber",
                    "id": item.id,
                    "scientific_name": sci,
                    "display_title": f"🔢 {item.designation} — {sci}",
                    "subtitle": item.trade_names or item.common_name_uz or item.common_name_en or "",
                    "score": 100 if clean.lower() in item.designation.lower() else 85,
                    "entity": item,
                })

        # 2. Species search (exact, token, fuzzy)
        sp_matches = await self.search(clean, limit=limit)
        for sp in sp_matches:
            if sp.id not in seen_species_ids:
                seen_species_ids.add(sp.id)
                trade_name = sp.trade_names[0].name if getattr(sp, "trade_names", None) and sp.trade_names else ""
                common_name = sp.common_names[0].name if getattr(sp, "common_names", None) and sp.common_names else ""
                subtitle = trade_name or common_name or sp.color_morphs or ""
                results.append({
                    "type": "species",
                    "id": sp.id,
                    "scientific_name": sp.scientific_name,
                    "display_title": f"🐠 {sp.scientific_name}",
                    "subtitle": subtitle,
                    "score": 95 if clean.lower() in sp.scientific_name.lower() else 80,
                    "entity": sp,
                })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    async def _fuzzy_search_species(self, query: str, limit: int = 15, threshold: float = 65.0) -> list[Species]:
        """In-memory fuzzy matching with rapidfuzz across species, trade names, common names, and synonyms."""
        stmt = (
            select(Species)
            .where(Species.is_published == True)
            .options(
                selectinload(Species.genus),
                selectinload(Species.common_names),
                selectinload(Species.trade_names),
                selectinload(Species.synonyms),
                selectinload(Species.localities),
            )
        )
        res = await self.session.execute(stmt)
        all_species = list(res.scalars().all())

        q_lower = query.lower()
        scored: list[tuple[float, Species]] = []

        for sp in all_species:
            candidates: list[str] = [sp.scientific_name.lower()]
            if sp.genus:
                candidates.append(sp.genus.scientific_name.lower())
            for tn in sp.trade_names:
                candidates.append(tn.name.lower())
            for cn in sp.common_names:
                candidates.append(cn.name.lower())
            for syn in sp.synonyms:
                candidates.append(syn.name.lower())
            for loc in sp.localities:
                candidates.append(loc.name.lower())
            if sp.color_morphs:
                candidates.append(sp.color_morphs.lower())

            best_score = 0.0
            for cand in candidates:
                # Calculate WRatio and token_sort_ratio
                s1 = fuzz.WRatio(q_lower, cand)
                s2 = fuzz.token_sort_ratio(q_lower, cand)
                score = max(s1, s2)
                if score > best_score:
                    best_score = score

            if best_score >= threshold:
                scored.append((best_score, sp))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [sp for _, sp in scored[:limit]]

    async def filter_search(self, **filters):
        results = await self.species_repo.filter_search(**filters)
        for sp in results:
            await self.species_repo.increment_search_count(sp.id)
        return results
