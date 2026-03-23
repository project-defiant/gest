BEGIN TRANSACTION;

/*
 Therapeutic areas table
 */
CREATE IF NOT EXISTS TABLE therapeutic_areas AS (
    (
        SELECT
            disease.id AS therapeuticAreaId,
            disease.name AS therapeuticAreaName,
        FROM
            disease
        WHERE
            length(disease.parents) = 0
    )
);

/*
 View to link therapeutic areas to diseases
 */
CREATE IF NOT EXISTS VIEW therapeutic_areas_lut AS (
    SELECT
        therapeuticAreaId,
        therapeuticAreaName,
        diseaseId,
        diseaseName
    FROM
        (
            SELECT
                disease.id AS diseaseId,
                disease.name AS diseaseName,
                unnest(disease.therapeuticAreas) AS therapeuticAreaId
            FROM
                disease
        )
        JOIN (
            SELECT
                therapeuticAreaId,
                therapeuticAreaName
            FROM
                therapeutic_areas
        ) USING (therapeuticAreaId)
);

END TRANSACTION;

SELECT
    COUNT(DISTINCT studyId) AS number_of_studies,
    '{release}' AS release,
    therapeuticArea
FROM
    study
WHERE
    studyType = 'gwas'
GROUP BY
    therapeuticArea
ORDER BY
    number_of_studies DESC;