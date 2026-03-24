SELECT
    COUNT(variantId) AS total_count_of_variants,
    '{release}' AS release
FROM
    variant;
