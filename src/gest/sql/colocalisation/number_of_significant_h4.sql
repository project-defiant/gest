SELECT
    COUNT(*) AS number_of_significant_h4,
    '{release}' AS release
FROM
    colocalisation
WHERE
    h4 >= 0.8;