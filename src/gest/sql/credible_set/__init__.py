"""Credible set SQL queries."""

from enum import Enum
from importlib.resources import files

from gest import Metadata, QueryFile

BASE_PATH = files("gest.sql.credible_set")


class CredibleSetQuery(Enum):
    """Enum representing the different credible set queries."""

    NUMBER_OF_CREDIBLE_SETS = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_credible_sets.sql")),
        metadata=Metadata(
            title="Number of credible sets",
            description="Number of distinct credible sets.",
        ),
    )

    TOTAL_COUNT_OF_CREDIBLE_SETS = QueryFile(
        file=str(BASE_PATH.joinpath("total_count_of_credible_sets.sql")),
        metadata=Metadata(
            title="Total count of credible sets",
            description="Total count of credible set rows.",
        ),
    )

    NUMBER_OF_CREDIBLE_SETS_PER_STUDY_TYPE = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_credible_sets_per_study_type.sql")),
        metadata=Metadata(
            title="Number of credible sets per study type",
            description="Number of distinct credible sets grouped by study type.",
        ),
    )

    NUMBER_OF_CREDIBLE_SETS_PER_PROJECT = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_credible_sets_per_project.sql")),
        metadata=Metadata(
            title="Number of credible sets per project",
            description="Number of distinct credible sets grouped by project.",
        ),
    )

    LOCUS_SIZE_STATS = QueryFile(
        file=str(BASE_PATH.joinpath("locus_size_stats.sql")),
        metadata=Metadata(
            title="Locus size statistics",
            description="Min, max, avg, median, and stddev of locus sizes.",
        ),
    )

    UNIQUE_LEAD_VARIANTS_PER_STUDY_TYPE = QueryFile(
        file=str(BASE_PATH.joinpath("unique_lead_variants_per_study_type.sql")),
        metadata=Metadata(
            title="Unique lead variants per study type",
            description="Number of distinct lead variants grouped by study type.",
        ),
    )

    UNIQUE_LEAD_VARIANTS_PER_PROJECT = QueryFile(
        file=str(BASE_PATH.joinpath("unique_lead_variants_per_project.sql")),
        metadata=Metadata(
            title="Unique lead variants per project",
            description="Number of distinct lead variants grouped by project.",
        ),
    )
