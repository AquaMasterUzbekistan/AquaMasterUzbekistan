"""Species repository with advanced queries."""

from __future__ import annotations

from sqlalchemy import select, or_, func, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.species import Species, CommonName, Synonym, TradeName, species_categories
from app.models.taxonomy import Subcategory, Genus


class SpeciesRepository(BaseRepository[Species]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Species)

    async def get_published(self, limit: int = 100, offset: int = 0) -> list[Species]:
        stmt = (
            select(Species)
            .where(Species.is_published == True)  # noqa: E712
            .order_by(Species.scientific_name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_scientific_name(self, name: str) -> Species | None:
        stmt = select(Species).where(
            func.lower(Species.scientific_name) == func.lower(name)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_subcategory(self, subcategory_id: int, limit: int = 100, offset: int = 0) -> list[Species]:
        stmt = (
            select(Species)
            .join(species_categories)
            .where(species_categories.c.subcategory_id == subcategory_id)
            .where(Species.is_published == True)  # noqa: E712
            .order_by(Species.scientific_name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_genus(self, genus_id: int, limit: int = 100, offset: int = 0) -> list[Species]:
        stmt = (
            select(Species)
            .where(Species.genus_id == genus_id)
            .where(Species.is_published == True)  # noqa: E712
            .order_by(Species.scientific_name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search(self, query: str, limit: int = 30) -> list[Species]:
        """Full-text search across scientific name, genus, family, locality, lake, common names, synonyms, trade names, notes."""
        from app.models.taxonomy import Genus, Family
        from app.models.locality import Locality, Lake
        q = f"%{query.lower()}%"
        stmt = (
            select(Species)
            .outerjoin(Species.genus)
            .outerjoin(Genus.family)
            .outerjoin(Species.localities)
            .outerjoin(Locality.lake)
            .outerjoin(CommonName, CommonName.species_id == Species.id)
            .outerjoin(Synonym, Synonym.species_id == Species.id)
            .outerjoin(TradeName, TradeName.species_id == Species.id)
            .where(
                Species.is_published == True,  # noqa: E712
                or_(
                    func.lower(Species.scientific_name).like(q),
                    func.lower(Genus.scientific_name).like(q),
                    func.lower(Family.scientific_name).like(q),
                    func.lower(Locality.name).like(q),
                    func.lower(Lake.name).like(q),
                    func.lower(CommonName.name).like(q),
                    func.lower(Synonym.name).like(q),
                    func.lower(TradeName.name).like(q),
                    func.lower(Species.taxonomic_notes).like(q),
                    func.lower(Species.color_morphs).like(q),
                    func.lower(Species.dietary_category).like(q),
                )
            )
            .distinct()
            .order_by(Species.scientific_name)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def filter_search(
        self,
        genus_name: str | None = None,
        family_name: str | None = None,
        lake_name: str | None = None,
        dietary_category: str | None = None,
        aggression: str | None = None,
        difficulty: str | None = None,
        breeding_type: str | None = None,
        origin_type: str | None = None,
        conservation_status: str | None = None,
        min_size: float | None = None,
        max_size: float | None = None,
        temp_target: float | None = None,
        ph_target: float | None = None,
        limit: int = 30,
        offset: int = 0,
    ) -> list[Species]:
        """Multi-parameter structured filter search (Section 16)."""
        from app.models.taxonomy import Genus, Family
        from app.models.locality import Locality, Lake

        stmt = (
            select(Species)
            .outerjoin(Species.genus)
            .outerjoin(Genus.family)
            .outerjoin(Species.localities)
            .outerjoin(Locality.lake)
            .where(Species.is_published == True)  # noqa: E712
        )

        if genus_name:
            stmt = stmt.where(func.lower(Genus.scientific_name) == genus_name.lower())
        if family_name:
            stmt = stmt.where(func.lower(Family.scientific_name) == family_name.lower())
        if lake_name:
            stmt = stmt.where(func.lower(Lake.name).like(f"%{lake_name.lower()}%"))
        if dietary_category:
            diet_stem = dietary_category.lower()
            if diet_stem.startswith("herbivor"):
                diet_stem = "herbivor"
            elif diet_stem.startswith("carnivor"):
                diet_stem = "carnivor"
            elif diet_stem.startswith("omnivor"):
                diet_stem = "omnivor"
            stmt = stmt.where(func.lower(Species.dietary_category).like(f"%{diet_stem}%"))
        if aggression:
            stmt = stmt.where(or_(
                Species.aggression == aggression,
                func.lower(cast(Species.aggression, String)).like(f"%{aggression.lower()}%")
            ))
        if difficulty:
            stmt = stmt.where(or_(
                Species.difficulty == difficulty,
                func.lower(cast(Species.difficulty, String)).like(f"%{difficulty.lower()}%")
            ))
        if breeding_type:
            stmt = stmt.where(Species.breeding_type == breeding_type)
        if origin_type:
            stmt = stmt.where(Species.origin_type == origin_type)
        if conservation_status:
            stmt = stmt.where(Species.conservation_status.ilike(f"%{conservation_status}%"))
        if min_size is not None:
            stmt = stmt.where(Species.max_size_cm >= min_size)
        if max_size is not None:
            stmt = stmt.where(Species.max_size_cm <= max_size)
        if temp_target is not None:
            stmt = stmt.where(Species.temp_min <= temp_target, Species.temp_max >= temp_target)
        if ph_target is not None:
            stmt = stmt.where(Species.ph_min <= ph_target, Species.ph_max >= ph_target)

        stmt = stmt.distinct().order_by(Species.scientific_name).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_most_viewed(self, limit: int = 10) -> list[Species]:
        stmt = (
            select(Species)
            .where(Species.is_published == True)  # noqa: E712
            .order_by(Species.view_count.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_view_count(self, species_id: int) -> None:
        sp = await self.get_by_id(species_id)
        if sp:
            sp.view_count += 1
            await self.session.commit()

    async def increment_search_count(self, species_id: int) -> None:
        sp = await self.get_by_id(species_id)
        if sp:
            sp.search_count += 1
            await self.session.commit()

    async def count_published(self) -> int:
        stmt = select(func.count()).select_from(Species).where(Species.is_published == True)  # noqa: E712
        result = await self.session.execute(stmt)
        return result.scalar_one()
