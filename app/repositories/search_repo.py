"""Repositories for localities, images, articles, aquariums, breeding."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.locality import Locality, Lake, Country, Continent
from app.models.image import SpeciesImage
from app.models.article import Article, ArticleCategory
from app.models.aquarium import UserAquarium, UserFish
from app.models.breeding import BreedingRecord
from app.models.health import HealthCondition
from app.models.dictionary import DictionaryTerm
from app.models.report import Report, IdentificationRequest
from app.models.taxonomy import Category, Subcategory, Family, Genus


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def get_top_level(self) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.parent_id == None)  # noqa: E711
            .order_by(Category.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, parent_id: int) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.parent_id == parent_id)
            .order_by(Category.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SubcategoryRepository(BaseRepository[Subcategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Subcategory)

    async def get_by_category(self, category_id: int) -> list[Subcategory]:
        stmt = (
            select(Subcategory)
            .where(Subcategory.category_id == category_id)
            .order_by(Subcategory.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class GenusRepository(BaseRepository[Genus]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Genus)

    async def get_by_family(self, family_id: int) -> list[Genus]:
        stmt = (
            select(Genus)
            .where(Genus.family_id == family_id)
            .order_by(Genus.scientific_name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_ordered(self, limit: int = 100, offset: int = 0) -> list[Genus]:
        stmt = (
            select(Genus)
            .order_by(Genus.scientific_name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_total(self) -> int:
        stmt = select(func.count(Genus.id))
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_by_name(self, name: str) -> Genus | None:
        stmt = select(Genus).where(func.lower(Genus.scientific_name) == func.lower(name.strip()))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_genus_stats(self, genus_id: int) -> dict[str, int]:
        from app.models.species import Species, ReliabilityLevel
        stmt = select(
            func.count(Species.id).label("total"),
            func.count(func.nullif(Species.reliability != ReliabilityLevel.SCIENTIFIC, True)).label("verified"),
        ).where(Species.genus_id == genus_id, Species.is_published == True)
        result = await self.session.execute(stmt)
        row = result.first()
        total = row.total if row else 0
        verified = row.verified if row else 0
        incomplete = max(0, total - verified)
        return {"total": total, "verified": verified, "incomplete": incomplete}


class FamilyRepository(BaseRepository[Family]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Family)

    async def get_all_ordered(self) -> list[Family]:
        stmt = select(Family).order_by(Family.scientific_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Family | None:
        stmt = select(Family).where(func.lower(Family.scientific_name) == func.lower(name.strip()))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_family_stats(self, family_id: int) -> dict[str, int]:
        from app.models.species import Species, ReliabilityLevel
        from app.models.taxonomy import Genus
        g_stmt = select(func.count(Genus.id)).where(Genus.family_id == family_id)
        g_res = await self.session.execute(g_stmt)
        genera_count = g_res.scalar_one() or 0

        sp_stmt = (
            select(
                func.count(Species.id).label("total"),
                func.count(func.nullif(Species.reliability != ReliabilityLevel.SCIENTIFIC, True)).label("verified"),
            )
            .join(Genus, Species.genus_id == Genus.id)
            .where(Genus.family_id == family_id, Species.is_published == True)
        )
        sp_res = await self.session.execute(sp_stmt)
        row = sp_res.first()
        total = row.total if row else 0
        verified = row.verified if row else 0
        incomplete = max(0, total - verified)
        return {
            "genera_count": genera_count,
            "total_species": total,
            "verified": verified,
            "incomplete": incomplete,
        }


class LocalityRepository(BaseRepository[Locality]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Locality)

    async def get_by_lake(self, lake_id: int) -> list[Locality]:
        stmt = (
            select(Locality)
            .where(Locality.lake_id == lake_id)
            .order_by(Locality.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_species_for_locality(self, locality_id: int) -> list:
        from app.models.species import Species, species_localities
        stmt = (
            select(Species)
            .join(species_localities, Species.id == species_localities.c.species_id)
            .where(species_localities.c.locality_id == locality_id)
            .order_by(Species.scientific_name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class LakeRepository(BaseRepository[Lake]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Lake)


class ImageRepository(BaseRepository[SpeciesImage]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SpeciesImage)

    async def get_by_species(self, species_id: int) -> list[SpeciesImage]:
        stmt = (
            select(SpeciesImage)
            .where(SpeciesImage.species_id == species_id)
            .order_by(SpeciesImage.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ArticleRepository(BaseRepository[Article]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Article)

    async def get_published(self, limit: int = 20, offset: int = 0) -> list[Article]:
        stmt = (
            select(Article)
            .where(Article.is_published == True)  # noqa: E712
            .order_by(Article.created_at.desc())
            .limit(limit).offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_category(self, category_id: int) -> list[Article]:
        stmt = (
            select(Article)
            .where(Article.category_id == category_id, Article.is_published == True)  # noqa: E712
            .order_by(Article.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ArticleCategoryRepository(BaseRepository[ArticleCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ArticleCategory)

    async def get_all_sorted(self) -> list[ArticleCategory]:
        stmt = select(ArticleCategory).order_by(ArticleCategory.sort_order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class AquariumRepository(BaseRepository[UserAquarium]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserAquarium)

    async def get_by_user(self, user_id: int) -> list[UserAquarium]:
        stmt = (
            select(UserAquarium)
            .where(UserAquarium.user_id == user_id)
            .order_by(UserAquarium.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class UserFishRepository(BaseRepository[UserFish]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserFish)

    async def get_by_aquarium(self, aquarium_id: int) -> list[UserFish]:
        stmt = (
            select(UserFish)
            .where(UserFish.aquarium_id == aquarium_id)
            .order_by(UserFish.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class BreedingRepository(BaseRepository[BreedingRecord]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BreedingRecord)

    async def get_by_user(self, user_id: int) -> list[BreedingRecord]:
        stmt = (
            select(BreedingRecord)
            .where(BreedingRecord.user_id == user_id)
            .order_by(BreedingRecord.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class HealthRepository(BaseRepository[HealthCondition]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HealthCondition)

    async def get_all_sorted(self) -> list[HealthCondition]:
        stmt = select(HealthCondition).order_by(HealthCondition.name_uz)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class DictionaryRepository(BaseRepository[DictionaryTerm]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DictionaryTerm)

    async def get_all_sorted(self) -> list[DictionaryTerm]:
        stmt = select(DictionaryTerm).order_by(DictionaryTerm.sort_order, DictionaryTerm.term)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search(self, query: str) -> list[DictionaryTerm]:
        q = f"%{query.lower()}%"
        stmt = (
            select(DictionaryTerm)
            .where(func.lower(DictionaryTerm.term).like(q))
            .order_by(DictionaryTerm.term)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Report)

    async def get_pending(self) -> list[Report]:
        stmt = (
            select(Report)
            .where(Report.status == "pending")
            .order_by(Report.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class IdentificationRequestRepository(BaseRepository[IdentificationRequest]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, IdentificationRequest)

    async def get_by_user(self, user_id: int) -> list[IdentificationRequest]:
        stmt = (
            select(IdentificationRequest)
            .where(IdentificationRequest.user_id == user_id)
            .order_by(IdentificationRequest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
