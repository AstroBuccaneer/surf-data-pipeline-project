-- ============================================
-- Surf Data Pipeline - Athena Rankings
-- Queries run against S3 data via Athena
-- ============================================

-- 1. Overall max wave height per location with benchmark comparison
SELECT
    location,
    MAX(wave_height_m)                          AS max_wave_height_m,
    ROUND(MAX(wave_height_m) * 3.28084, 2)      AS max_wave_height_ft,
    ROUND(MAX(pct_of_nazare), 2)                AS pct_of_nazare,
    ROUND(MAX(pct_of_lituya), 2)                AS pct_of_lituya
FROM "surf_pipeline_db"."buoy_data_transformed"
WHERE wave_height_m IS NOT NULL
GROUP BY location
ORDER BY max_wave_height_m DESC;


-- 2. Seasonal rankings using window functions
SELECT
    location,
    season,
    ROUND(AVG(wave_height_m), 2)                AS avg_wave_height_m,
    ROUND(MAX(wave_height_m), 2)                AS max_wave_height_m,
    COUNT(*)                                    AS total_readings,
    RANK() OVER (
        PARTITION BY season
        ORDER BY AVG(wave_height_m) DESC
    )                                           AS season_rank
FROM "surf_pipeline_db"."buoy_data_transformed"
WHERE wave_height_m IS NOT NULL
GROUP BY location, season
ORDER BY season, season_rank;


-- 3. Hurricane season vs non hurricane season using CTE
WITH hurricane AS (
    SELECT
        location,
        ROUND(AVG(wave_height_m), 2)            AS avg_wave_height_m
    FROM "surf_pipeline_db"."buoy_data_transformed"
    WHERE is_hurricane_season = 'Yes'
    AND wave_height_m IS NOT NULL
    GROUP BY location
),
non_hurricane AS (
    SELECT
        location,
        ROUND(AVG(wave_height_m), 2)            AS avg_wave_height_m
    FROM "surf_pipeline_db"."buoy_data_transformed"
    WHERE is_hurricane_season = 'No'
    AND wave_height_m IS NOT NULL
    GROUP BY location
)
SELECT
    h.location,
    h.avg_wave_height_m                         AS hurricane_season_avg,
    n.avg_wave_height_m                         AS non_hurricane_avg,
    ROUND(h.avg_wave_height_m -
          n.avg_wave_height_m, 2)               AS difference
FROM hurricane h
JOIN non_hurricane n ON h.location = n.location
ORDER BY difference DESC;


-- 4. Top 10 highest wave events
SELECT
    location,
    wave_height_m,
    ROUND(wave_height_m * 3.28084, 2)           AS wave_height_ft,
    ROUND(pct_of_nazare, 2)                     AS pct_of_nazare,
    ROW_NUMBER() OVER (
        ORDER BY wave_height_m DESC
    )                                           AS overall_rank
FROM "surf_pipeline_db"."buoy_data_transformed"
WHERE wave_height_m IS NOT NULL
LIMIT 10;