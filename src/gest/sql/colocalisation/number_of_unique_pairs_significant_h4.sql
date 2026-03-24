SELECT
    COUNT(DISTINCT (leftStudyLocusId, rightStudyLocusId)) AS number_of_unique_pairs_significant_h4,
    '{release}' AS release
FROM
    colocalisation
WHERE
    h4 > 0.8;
