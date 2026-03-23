"""Colocalisation SQL queries."""

from enum import Enum
from importlib.resources import files

from gest import Metadata, QueryFile

BASE_PATH = files("gest.sql.colocalisation")


class ColocalisationQuery(Enum):
    """Enum representing the different colocalisation queries."""

    NUMBER_OF_SIGNIFICANT_H4 = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_significant_h4.sql")),
        metadata=Metadata(
            title="Number of significant H4",
            description="Number of significant H4 colocalisations.",
        ),
    )

    NUMBER_OF_SIGNIFICANT_CLPP = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_significant_clpp.sql")),
        metadata=Metadata(
            title="Number of significant CLPP",
            description="Number of significant CLPP colocalisations.",
        ),
    )
