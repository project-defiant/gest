SELECT
    COUNT(*) AS number_of_significant_h4,
    '{release}' AS release,
    rightStudyType
FROM
    colocalisation
WHERE
    h4 > 0.8
GROUP BY
    rightStudyType
ORDER BY
    number_of_significant_h4 DESC;
