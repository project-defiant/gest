WITH genes_per_locus AS (
    SELECT
        studyLocusId,
        COUNT(DISTINCT geneId) AS gene_count
    FROM
        l2g_prediction
    GROUP BY
        studyLocusId
)
SELECT
    gene_count,
    COUNT(*) AS number_of_study_loci,
    '{release}' AS release
FROM
    genes_per_locus
GROUP BY
    gene_count
ORDER BY
    gene_count;
