SELECT
    COUNT(*) AS number_of_significant_clpp,
    '{release}' AS release
FROM
    colocalisation
WHERE
    clpp >= 0.01;