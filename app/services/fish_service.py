"""Fish service — business logic for species browsing, search, comparison."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import SpeciesRepository, SubcategoryRepository, GenusRepository, CategoryRepository
from app.models.species import Species


class FishService:
    """Central service for fish atlas operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.species_repo = SpeciesRepository(session)
        self.subcategory_repo = SubcategoryRepository(session)
        self.genus_repo = GenusRepository(session)
        self.category_repo = CategoryRepository(session)

    async def get_species(self, species_id: int) -> Species | None:
        sp = await self.species_repo.get_by_id(species_id)
        if sp:
            await self.species_repo.increment_view_count(species_id)
        return sp

    async def get_species_by_subcategory(
        self, subcategory_id: int, limit: int = 100, offset: int = 0
    ) -> list[Species]:
        return await self.species_repo.get_by_subcategory(subcategory_id, limit, offset)

    async def get_species_by_genus(
        self, genus_id: int, limit: int = 100, offset: int = 0
    ) -> list[Species]:
        return await self.species_repo.get_by_genus(genus_id, limit, offset)

    async def get_top_categories(self):
        return await self.category_repo.get_top_level()

    async def get_subcategories(self, category_id: int):
        return await self.subcategory_repo.get_by_category(category_id)

    async def get_genera_by_family(self, family_id: int):
        return await self.genus_repo.get_by_family(family_id)
