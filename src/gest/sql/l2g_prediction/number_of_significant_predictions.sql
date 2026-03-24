SELECT
    COUNT(*) AS number_of_significant_predictions,
    '{release}' AS release
FROM
    l2g_prediction
WHERE
    score >= 0.05;
