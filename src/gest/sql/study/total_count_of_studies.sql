SELECT
    COUNT(studyId) AS total_count_of_studies,
    '{release}' AS release
FROM
    study;
