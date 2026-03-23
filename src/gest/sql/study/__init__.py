"""Study SQL queries."""

from enum import Enum
from importlib.resources import files

from gest import Metadata, QueryFile

BASE_PATH = files("gest.sql.study")


class StudyQuery(Enum):
    """Enum representing the different study queries."""

    NUMBER_OF_GWAS_STUDIES = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_gwas_studies.sql")),
        metadata=Metadata(
            title="Number of GWAS studies",
            description="Number of GWAS studies in the database.",
        ),
    )

    NUMBER_OF_GWAS_STUDIES_PER_PROJECT = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_gwas_studies_per_project.sql")),
        metadata=Metadata(
            title="Number of GWAS studies per project",
            description="Number of GWAS studies per project in the database.",
        ),
    )

    NUMBER_OF_GWAS_STUDIES_PER_STUDY_TYPE = QueryFile(
        file=str(BASE_PATH.joinpath("number_of_gwas_studies_per_study_type.sql")),
        metadata=Metadata(
            title="Number of GWAS studies per study type",
            description="Number of GWAS studies per study type in the database.",
        ),
    )
