"""Colocalisation SQL queries."""

from enum import Enum
from importlib.resources import files

from gest import Metadata, QueryFile

BASE_PATH = files("gest.sql.colocalisation")


class ColocalisationQuery(Enum):
    """Enum representing the different colocalisation queries."""

    TOTAL_COUNT_OF_COLOCALISATIONS = QueryFile(
        file=str(BASE_PATH.joinpath("total_count_of_colocalisations.sql")),
        metadata=Metadata(
            title="Total count of colocalisations",
            description="Total count of colocalisation rows.",
        ),
    )

    NUMBER_OF_SIGNIFICANT_CLPP = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_significant_clpp.sql")),
        metadata=Metadata(
            title="Number of significant CLPP",
            description="Number of significant CLPP colocalisations (clpp >= 0.01).",
        ),
    )

    NUMBER_OF_SIGNIFICANT_H4 = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_significant_h4.sql")),
        metadata=Metadata(
            title="Number of significant H4",
            description="Number of significant H4 colocalisations (h4 > 0.8).",
        ),
    )

    NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_CLPP = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_unique_pairs_significant_clpp.sql")),
        metadata=Metadata(
            title="Number of unique pairs with significant CLPP",
            description="Number of distinct study locus pairs with clpp >= 0.01.",
        ),
    )

    NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_H4 = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_unique_pairs_significant_h4.sql")),
        metadata=Metadata(
            title="Number of unique pairs with significant H4",
            description="Number of distinct study locus pairs with h4 > 0.8.",
        ),
    )

    NUMBER_OF_SIGNIFICANT_CLPP_PER_STUDY_TYPE = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_significant_clpp_per_study_type.sql")),
        metadata=Metadata(
            title="Number of significant CLPP per study type",
            description="Significant CLPP colocalisations grouped by right study type.",
        ),
    )

    NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_CLPP_PER_STUDY_TYPE = QueryFile(
        file=str(
            BASE_PATH.joinpath(
                "number_of_unique_pairs_significant_clpp_per_study_type.sql"
            )
        ),
        metadata=Metadata(
            title="Unique pairs with significant CLPP per study type",
            description="Distinct study locus pairs with clpp >= 0.01 grouped by right study type.",
        ),
    )

    NUMBER_OF_SIGNIFICANT_H4_PER_STUDY_TYPE = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_significant_h4_per_study_type.sql")),
        metadata=Metadata(
            title="Number of significant H4 per study type",
            description="Significant H4 colocalisations grouped by right study type.",
        ),
    )

    NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_H4_PER_STUDY_TYPE = QueryFile(
        file=str(
            BASE_PATH.joinpath(
                "number_of_unique_pairs_significant_h4_per_study_type.sql"
            )
        ),
        metadata=Metadata(
            title="Unique pairs with significant H4 per study type",
            description="Distinct study locus pairs with h4 > 0.8 grouped by right study type.",
        ),
    )
