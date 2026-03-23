SELECT
    COUNT(DISTINCT studyId) AS number_of_studies,
    '{release}' AS release,
    projectId
FROM
    study
GROUP BY
    projectId
ORDER BY
    number_of_studies DESC;