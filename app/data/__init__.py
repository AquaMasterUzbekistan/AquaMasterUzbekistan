"""Structured authoritative fish datasets for AquaMasterUzbekistan Atlas.

Aggregates all regional dataset modules for Lake Malawi, Lake Tanganyika,
Lake Victoria, Other African cichlids, American cichlids, Discus, and Other freshwater fish.
"""

from __future__ import annotations

from app.data.malawi_data import MALAWI_GENERA, MALAWI_SPECIES
from app.data.tanganyika_data import TANGANYIKA_GENERA, TANGANYIKA_SPECIES
from app.data.victoria_other_africa_data import VICTORIA_AFRICA_GENERA, VICTORIA_AFRICA_SPECIES
from app.data.american_cichlids_data import AMERICAN_GENERA, AMERICAN_SPECIES
from app.data.discus_data import DISCUS_GENERA, DISCUS_SPECIES
from app.data.other_freshwater_data import OTHER_FRESHWATER_GENERA, OTHER_FRESHWATER_SPECIES
from app.data.expanded_species_data import (
    EXPANDED_AMERICAN_SPECIES,
    EXPANDED_VICTORIA_AFRICA_SPECIES,
    EXPANDED_OTHER_FRESHWATER_SPECIES,
)

ALL_GENERA = (
    MALAWI_GENERA
    + TANGANYIKA_GENERA
    + VICTORIA_AFRICA_GENERA
    + AMERICAN_GENERA
    + DISCUS_GENERA
    + OTHER_FRESHWATER_GENERA
)

ALL_SPECIES = (
    MALAWI_SPECIES
    + TANGANYIKA_SPECIES
    + VICTORIA_AFRICA_SPECIES
    + EXPANDED_VICTORIA_AFRICA_SPECIES
    + AMERICAN_SPECIES
    + EXPANDED_AMERICAN_SPECIES
    + DISCUS_SPECIES
    + OTHER_FRESHWATER_SPECIES
    + EXPANDED_OTHER_FRESHWATER_SPECIES
)

__all__ = [
    "MALAWI_GENERA",
    "MALAWI_SPECIES",
    "TANGANYIKA_GENERA",
    "TANGANYIKA_SPECIES",
    "VICTORIA_AFRICA_GENERA",
    "VICTORIA_AFRICA_SPECIES",
    "AMERICAN_GENERA",
    "AMERICAN_SPECIES",
    "DISCUS_GENERA",
    "DISCUS_SPECIES",
    "OTHER_FRESHWATER_GENERA",
    "OTHER_FRESHWATER_SPECIES",
    "ALL_GENERA",
    "ALL_SPECIES",
]
