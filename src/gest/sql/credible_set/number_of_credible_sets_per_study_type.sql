SELECT
    COUNT(DISTINCT studyLocusId) AS number_of_credible_sets,
    '{release}' AS release,
    studyType
FROM
    credible_set
GROUP BY
    studyType
ORDER BY
    number_of_credible_sets DESC;
