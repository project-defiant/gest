"""Variant SQL queries."""

from enum import Enum
from importlib.resources import files

from gest import Metadata, QueryFile

BASE_PATH = files("gest.sql.variant")


class VariantQuery(Enum):
    """Enum representing the different variant queries."""

    NUMBER_OF_VARIANTS = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_variants.sql")),
        metadata=Metadata(
            title="Number of variants",
            description="Number of distinct variants.",
        ),
    )

    TOTAL_COUNT_OF_VARIANTS = QueryFile(
        file=str(BASE_PATH.joinpath("total_count_of_variants.sql")),
        metadata=Metadata(
            title="Total count of variants",
            description="Total count of variant rows.",
        ),
    )

    VARIANTS_PER_MAX_EFFECT_ASSESSMENT = QueryFile(
        file=str(BASE_PATH.joinpath("variants_per_max_effect_assessment.sql")),
        metadata=Metadata(
            title="Variants per max effect assessment",
            description="Number of variants grouped by their highest-scoring effect assessment.",
        ),
    )
