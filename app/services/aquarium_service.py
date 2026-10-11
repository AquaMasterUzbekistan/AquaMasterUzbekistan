"""User aquarium management service."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import AquariumRepository, UserFishRepository


class AquariumService:
    def __init__(self, session: AsyncSession):
        self.aquarium_repo = AquariumRepository(session)
        self.fish_repo = UserFishRepository(session)

    async def get_user_aquariums(self, user_id: int):
        return await self.aquarium_repo.get_by_user(user_id)

    async def create_aquarium(self, user_id: int, name: str, volume: float | None = None):
        return await self.aquarium_repo.create(
            user_id=user_id, name=name, volume_liters=volume
        )

    async def get_aquarium_fish(self, aquarium_id: int):
        return await self.fish_repo.get_by_aquarium(aquarium_id)

    async def add_fish(self, aquarium_id: int, species_id: int | None = None,
                       custom_name: str | None = None, males: int = 0,
                       females: int = 0, unknown: int = 0):
        return await self.fish_repo.create(
            aquarium_id=aquarium_id,
            species_id=species_id,
            custom_name=custom_name,
            quantity_male=males,
            quantity_female=females,
            quantity_unknown=unknown,
        )

    async def delete_aquarium(self, aquarium_id: int) -> bool:
        return await self.aquarium_repo.delete(aquarium_id)
