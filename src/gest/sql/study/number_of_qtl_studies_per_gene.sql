SELECT
    COUNT(DISTINCT studyId) AS number_of_studies,
    '{release}' AS release,
    geneId
FROM
    study
WHERE
    studyType != 'gwas'
GROUP BY
    geneId
ORDER BY
    number_of_studies DESC;