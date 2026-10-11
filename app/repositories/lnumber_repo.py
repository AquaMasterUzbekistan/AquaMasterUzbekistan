"""L-number and LDA-number catfish repository."""

from __future__ import annotations

import re
from sqlalchemy import select, or_, func, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.lnumber import LNumberDesignation, lnumber_species


class LNumberRepository(BaseRepository[LNumberDesignation]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, LNumberDesignation)

    async def get_by_designation(self, designation: str) -> LNumberDesignation | None:
        """Find designation by exact or normalized code (e.g. L046, L-46, L 46, LDA 016)."""
        clean = designation.strip().upper()
        # Normalization attempts
        candidates = [clean, clean.replace(" ", ""), clean.replace("-", "")]
        m = re.match(r"^(L|LDA)\s*[-_]?\s*0*(\d+)$", clean)
        if m:
            prefix, num = m.groups()
            padded = f"{prefix}{int(num):03d}"
            unpadded = f"{prefix}{int(num)}"
            candidates.extend([padded, unpadded])

        stmt_exact = (
            select(LNumberDesignation)
            .options(selectinload(LNumberDesignation.species_list))
            .where(func.upper(LNumberDesignation.designation).in_(candidates))
        )
        res_exact = await self.session.execute(stmt_exact)
        item = res_exact.scalars().first()
        if item:
            return item

        # Fallback to alternative numbers
        stmt_alt = (
            select(LNumberDesignation)
            .options(selectinload(LNumberDesignation.species_list))
            .where(func.upper(LNumberDesignation.alternative_numbers).like(f"%{clean}%"))
        )
        res_alt = await self.session.execute(stmt_alt)
        return res_alt.scalars().first()

    async def get_all_paged(
        self,
        number_type: str | None = None,
        only_ancistrus: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[LNumberDesignation]:
        stmt = (
            select(LNumberDesignation)
            .options(selectinload(LNumberDesignation.species_list))
        )
        if number_type:
            stmt = stmt.where(LNumberDesignation.number_type == number_type.upper())
        if only_ancistrus:
            stmt = stmt.where(LNumberDesignation.is_ancistrus == True)  # noqa: E712
        stmt = stmt.order_by(LNumberDesignation.number_type, LNumberDesignation.code_number).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_total(
        self,
        number_type: str | None = None,
        only_ancistrus: bool = False,
    ) -> int:
        stmt = select(func.count(LNumberDesignation.id))
        if number_type:
            stmt = stmt.where(LNumberDesignation.number_type == number_type.upper())
        if only_ancistrus:
            stmt = stmt.where(LNumberDesignation.is_ancistrus == True)  # noqa: E712
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def search(self, query: str, limit: int = 30) -> list[LNumberDesignation]:
        """Search by designation, alternative numbers, scientific name, common names, river basin."""
        q = f"%{query.strip().lower()}%"
        stmt = (
            select(LNumberDesignation)
            .options(selectinload(LNumberDesignation.species_list))
            .where(
                or_(
                    func.lower(LNumberDesignation.designation).like(q),
                    func.lower(LNumberDesignation.alternative_numbers).like(q),
                    func.lower(LNumberDesignation.scientific_name_current).like(q),
                    func.lower(LNumberDesignation.genus_name).like(q),
                    func.lower(LNumberDesignation.common_name_uz).like(q),
                    func.lower(LNumberDesignation.common_name_en).like(q),
                    func.lower(LNumberDesignation.common_name_ru).like(q),
                    func.lower(LNumberDesignation.trade_names).like(q),
                    func.lower(LNumberDesignation.river_basin).like(q),
                    func.lower(LNumberDesignation.country).like(q),
                )
            )
            .order_by(LNumberDesignation.number_type, LNumberDesignation.code_number)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def link_species(
        self,
        lnumber_id: int,
        species_id: int,
        is_primary: bool = True,
        notes: str | None = None,
    ) -> None:
        # Check if already linked
        check_stmt = select(lnumber_species).where(
            lnumber_species.c.lnumber_id == lnumber_id,
            lnumber_species.c.species_id == species_id,
        )
        res = await self.session.execute(check_stmt)
        if not res.first():
            ins = insert(lnumber_species).values(
                lnumber_id=lnumber_id,
                species_id=species_id,
                is_primary=is_primary,
                notes=notes,
            )
            await self.session.execute(ins)
            await self.session.flush()
