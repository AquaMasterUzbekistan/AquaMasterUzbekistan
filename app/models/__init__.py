"""Models package — import all models to ensure metadata registration."""

from app.models.user import User, Favorite, RecentlyViewed, RoleName, UserActivityLog
from app.models.taxonomy import Category, Subcategory, Family, Genus
from app.models.species import (
    Species, CommonName, Synonym, TradeName,
    ReliabilityLevel, AggressionLevel, DifficultyLevel,
    BreedingType, WaterType, OriginType,
    species_localities, species_categories,
)
from app.models.locality import Continent, Country, Lake, Locality
from app.models.image import SpeciesImage, ImageType, VerificationStatus
from app.models.compatibility import Compatibility, SimilarSpecies, CompatibilityLevel
from app.models.genetics import GeneticsMorph
from app.models.source import (
    Source, SpeciesSource, ConfidenceLevel,
    ScientificClaim, VerificationHistory, ImportLog,
)
from app.models.aquarium import UserAquarium, UserFish
from app.models.breeding import BreedingRecord
from app.models.health import HealthCondition
from app.models.article import Article, ArticleCategory
from app.models.dictionary import DictionaryTerm
from app.models.report import (
    Report, IdentificationRequest, AdminLog,
    ReportType, ReportStatus,
)
from app.models.lnumber import LNumberDesignation, lnumber_species

__all__ = [
    "User", "Favorite", "RecentlyViewed", "RoleName", "UserActivityLog",
    "Category", "Subcategory", "Family", "Genus",
    "Species", "CommonName", "Synonym", "TradeName",
    "ReliabilityLevel", "AggressionLevel", "DifficultyLevel",
    "BreedingType", "WaterType", "OriginType",
    "species_localities", "species_categories",
    "Continent", "Country", "Lake", "Locality",
    "SpeciesImage", "ImageType", "VerificationStatus",
    "Compatibility", "SimilarSpecies", "CompatibilityLevel",
    "GeneticsMorph",
    "Source", "SpeciesSource", "ConfidenceLevel",
    "ScientificClaim", "VerificationHistory", "ImportLog",
    "UserAquarium", "UserFish",
    "BreedingRecord",
    "HealthCondition",
    "Article", "ArticleCategory",
    "DictionaryTerm",
    "Report", "IdentificationRequest", "AdminLog",
    "ReportType", "ReportStatus",
    "LNumberDesignation", "lnumber_species",
]
