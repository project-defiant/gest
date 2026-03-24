SELECT
    COUNT(DISTINCT variantId) AS unique_lead_variants,
    '{release}' AS release,
    studyType
FROM
    credible_set
GROUP BY
    studyType
ORDER BY
    unique_lead_variants DESC;
