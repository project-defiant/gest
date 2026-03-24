SELECT
    COUNT(studyLocusId) AS total_count_of_credible_sets,
    '{release}' AS release
FROM
    credible_set;
