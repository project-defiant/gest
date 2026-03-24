SELECT
    COUNT(DISTINCT cs.studyLocusId) AS number_of_credible_sets,
    '{release}' AS release,
    s.projectId
FROM
    credible_set cs
    INNER JOIN study s USING (studyId)
GROUP BY
    s.projectId
ORDER BY
    number_of_credible_sets DESC;
