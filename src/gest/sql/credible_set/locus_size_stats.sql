SELECT
    MIN(len(locus)) AS min_locus_size,
    MAX(len(locus)) AS max_locus_size,
    AVG(len(locus)) AS avg_locus_size,
    MEDIAN(len(locus)) AS median_locus_size,
    STDDEV(len(locus)) AS stddev_locus_size,
    '{release}' AS release
FROM
    credible_set;
