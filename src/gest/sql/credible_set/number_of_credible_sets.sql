SELECT
    COUNT(DISTINCT studyLocusId) AS number_of_credible_sets,
    '{release}' AS release
FROM
    credible_set;
