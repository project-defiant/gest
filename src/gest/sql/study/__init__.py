"""Study SQL queries."""

from enum import Enum
from importlib.resources import files

from gest import Metadata, QueryFile

BASE_PATH = files("gest.sql.study")


class StudyQuery(Enum):
    """Enum representing the different study queries."""

    NUMBER_OF_STUDIES = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_studies.sql")),
        metadata=Metadata(
            title="Number of studies",
            description="Number of distinct studies in the database.",
        ),
    )

    TOTAL_COUNT_OF_STUDIES = QueryFile(
        file=str(BASE_PATH.joinpath("total_count_of_studies.sql")),
        metadata=Metadata(
            title="Total count of studies",
            description="Total count of study rows in the database.",
        ),
    )

    NUMBER_OF_STUDIES_PER_STUDY_TYPE = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_studies_per_study_type.sql")),
        metadata=Metadata(
            title="Number of studies per study type",
            description="Number of distinct studies grouped by study type.",
        ),
    )
