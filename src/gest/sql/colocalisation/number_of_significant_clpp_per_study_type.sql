SELECT
    COUNT(*) AS number_of_significant_clpp,
    '{release}' AS release,
    rightStudyType
FROM
    colocalisation
WHERE
    clpp >= 0.01
GROUP BY
    rightStudyType
ORDER BY
    number_of_significant_clpp DESC;
