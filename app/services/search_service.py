"""Search service with fuzzy matching."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import SpeciesRepository, LNumberRepository
from app.utils.validators import sanitize_search_query


class SearchService:
    def __init__(self, session: AsyncSession):
        self.species_repo = SpeciesRepository(session)
        self.lnumber_repo = LNumberRepository(session)

    async def search(self, query: str, limit: int = 20):
        clean = sanitize_search_query(query)
        if len(clean) < 2:
            return []
        results = await self.species_repo.search(clean, limit)
        # Increment search counts
        for sp in results:
            await self.species_repo.increment_search_count(sp.id)
        return results

    async def search_lnumbers(self, query: str, limit: int = 15):
        clean = sanitize_search_query(query)
        if len(clean) < 2:
            return []
        exact = await self.lnumber_repo.get_by_designation(clean)
        if exact:
            return [exact]
        return await self.lnumber_repo.search(clean, limit)

    async def filter_search(self, **filters):
        results = await self.species_repo.filter_search(**filters)
        for sp in results:
            await self.species_repo.increment_search_count(sp.id)
        return results
