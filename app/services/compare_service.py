"""Comparison service."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import SpeciesRepository
from app.models.species import Species
from app.utils.formatting import format_comparison


class CompareService:
    def __init__(self, session: AsyncSession):
        self.species_repo = SpeciesRepository(session)

    async def compare(self, *species_ids: int) -> str | None:
        species_list = []
        for s_id in species_ids:
            sp = await self.species_repo.get_by_id(s_id)
            if sp:
                sp.compare_count += 1
                species_list.append(sp)
        if len(species_list) < 2:
            return None
        await self.species_repo.session.commit()
        return format_comparison(*species_list)
