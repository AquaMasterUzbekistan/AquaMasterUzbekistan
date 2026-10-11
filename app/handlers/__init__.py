"""Handlers package — register all routers."""

from app.handlers.start import router as start_router
from app.handlers.african_cichlids import router as african_router
from app.handlers.american_cichlids import router as american_router
from app.handlers.discus import router as discus_router
from app.handlers.other_fish import router as other_fish_router
from app.handlers.fish_profile import router as profile_router
from app.handlers.search import router as search_router
from app.handlers.fish_images import router as fish_images_router
from app.handlers.compare import router as compare_router
from app.handlers.calculators import router as calculators_router
from app.handlers.my_aquarium import router as aquarium_router
from app.handlers.remaining import (
    breeding_router, health_router, genetics_router,
    locality_router, articles_router,
    dictionary_router, about_router, favorites_router,
    reports_router,
)
from app.handlers.lnumber import router as lnumber_router
from app.handlers.taxonomy import router as taxonomy_router
from app.handlers.admin import admin_router

all_routers = [
    start_router,
    taxonomy_router,
    lnumber_router,
    african_router,
    american_router,
    discus_router,
    other_fish_router,
    profile_router,
    search_router,
    fish_images_router,
    compare_router,
    calculators_router,
    aquarium_router,
    breeding_router,
    health_router,
    genetics_router,
    locality_router,
    articles_router,
    dictionary_router,
    about_router,
    favorites_router,
    reports_router,
    admin_router,
]
