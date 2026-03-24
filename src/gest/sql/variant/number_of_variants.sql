SELECT
    COUNT(DISTINCT variantId) AS number_of_variants,
    '{release}' AS release
FROM
    variant;
