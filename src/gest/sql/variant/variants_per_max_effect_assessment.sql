WITH unnested AS (
    SELECT
        variantId,
        unnest(variantEffect) AS effect
    FROM
        variant
),
max_scores AS (
    SELECT
        variantId,
        arg_max(effect.assessment, effect.score) AS max_assessment
    FROM
        unnested
    GROUP BY
        variantId
)
SELECT
    COUNT(*) AS number_of_variants,
    '{release}' AS release,
    max_assessment
FROM
    max_scores
GROUP BY
    max_assessment
ORDER BY
    number_of_variants DESC;
