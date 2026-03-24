SELECT
    COUNT(DISTINCT cs.variantId) AS unique_lead_variants,
    '{release}' AS release,
    s.projectId
FROM
    credible_set cs
    INNER JOIN study s USING (studyId)
GROUP BY
    s.projectId
ORDER BY
    unique_lead_variants DESC;
