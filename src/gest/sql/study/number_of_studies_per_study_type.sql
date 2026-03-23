SELECT
    COUNT(DISTINCT studyId) AS number_of_studies,
    '{release}' AS release,
    studyType
FROM
    study
GROUP BY
    studyType
ORDER BY
    number_of_studies DESC;