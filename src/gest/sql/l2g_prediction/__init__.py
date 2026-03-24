"""L2G prediction SQL queries."""

from enum import Enum
from importlib.resources import files

from gest import Metadata, QueryFile

BASE_PATH = files("gest.sql.l2g_prediction")


class L2GPredictionQuery(Enum):
    """Enum representing the different L2G prediction queries."""

    TOTAL_COUNT_OF_PREDICTIONS = QueryFile(
        file=str(BASE_PATH.joinpath("total_count_of_predictions.sql")),
        metadata=Metadata(
            title="Total count of predictions",
            description="Total count of L2G prediction rows.",
        ),
    )

    NUMBER_OF_SIGNIFICANT_PREDICTIONS = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_significant_predictions.sql")),
        metadata=Metadata(
            title="Number of significant predictions",
            description="Number of L2G predictions with score >= 0.05.",
        ),
    )

    GENE_COUNT_PER_STUDY_LOCUS = QueryFile(
        file=str(BASE_PATH.joinpath("gene_count_per_study_locus.sql")),
        metadata=Metadata(
            title="Gene count per study locus",
            description="Distribution of distinct gene counts per study locus.",
        ),
    )
