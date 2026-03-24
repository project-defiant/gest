SELECT
    COUNT(DISTINCT (leftStudyLocusId, rightStudyLocusId)) AS number_of_unique_pairs_significant_clpp,
    '{release}' AS release
FROM
    colocalisation
WHERE
    clpp >= 0.01;
