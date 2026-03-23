SELECT
    COUNT(DISTINCT studyId) AS number_of_studies,
    '{release}' AS release
FROM
    study;