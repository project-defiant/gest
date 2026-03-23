SELECT
    DISTINCT COUNT(*) AS number_of_significant_clpp,
    '{release}' AS release
FROM
    colocalisation
WHERE
    h4 >= 0.8;