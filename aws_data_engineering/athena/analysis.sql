-- ============================================
-- Surf Data Pipeline - Athena Deep Analysis
-- Queries run against S3 data via Athena
-- ============================================

-- 1. Year over year wave height trend with rolling average
WITH yearly_avg AS (
    SELECT
        location,
        year,
        ROUND(AVG(wave_height_m), 2)            AS avg_wave_height_m
    FROM "surf_pipeline_db"."buoy_data_transformed"
    WHERE wave_height_m IS NOT NULL
    GROUP BY location, year
)
SELECT
    location,
    year,
    avg_wave_height_m,
    ROUND(AVG(avg_wave_height_m) OVER (
        PARTITION BY location
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                                       AS rolling_3yr_avg,
    RANK() OVER (
        PARTITION BY location
        ORDER BY avg_wave_height_m DESC
    )                                           AS year_rank
FROM yearly_avg
ORDER BY location, year;


-- 2. Best month to surf at each location
WITH monthly_avg AS (
    SELECT
        location,
        month,
        ROUND(AVG(wave_height_m), 2)            AS avg_wave_height_m,
        SUM(CASE WHEN wave_height_m >= 1.5
            THEN 1 ELSE 0 END)                  AS surfable_days,
        COUNT(*)                                AS total_readings
    FROM "surf_pipeline_db"."buoy_data_transformed"
    WHERE wave_height_m IS NOT NULL
    GROUP BY location, month
)
SELECT
    location,
    month,
    avg_wave_height_m,
    surfable_days,
    RANK() OVER (
        PARTITION BY location
        ORDER BY avg_wave_height_m DESC
    )                                           AS best_month_rank
FROM monthly_avg
ORDER BY location, best_month_rank;


-- 3. Nazare benchmark gap analysis
WITH nazare_comparison AS (
    SELECT
        location,
        MAX(pct_of_nazare)                      AS closest_pct_to_nazare,
        MAX(wave_height_m)                      AS max_wave_m,
        ROUND(MAX(wave_height_m)
            * 3.28084, 2)                       AS max_wave_ft,
        26.2 - MAX(wave_height_m)               AS gap_to_nazare_m
    FROM "surf_pipeline_db"."buoy_data_transformed"
    WHERE wave_height_m IS NOT NULL
    GROUP BY location
)
SELECT
    location,
    max_wave_ft,
    ROUND(closest_pct_to_nazare, 2)             AS pct_of_nazare,
    ROUND(gap_to_nazare_m, 2)                   AS gap_to_nazare_m,
    ROUND(gap_to_nazare_m * 3.28084, 2)         AS gap_to_nazare_ft,
    RANK() OVER (
        ORDER BY closest_pct_to_nazare DESC
    )                                           AS nazare_rank
FROM nazare_comparison
ORDER BY nazare_rank;


-- 4. Surfable wave frequency by quarter
SELECT
    location,
    quarter,
    COUNT(*)                                    AS total_readings,
    SUM(CASE WHEN wave_height_m >= 1.5
        THEN 1 ELSE 0 END)                      AS surfable_readings,
    ROUND(SUM(CASE WHEN wave_height_m >= 1.5
        THEN 1 ELSE 0 END) * 100.0
        / COUNT(*), 2)                          AS surfable_pct,
    RANK() OVER (
        PARTITION BY quarter
        ORDER BY SUM(CASE WHEN wave_height_m >= 1.5
            THEN 1 ELSE 0 END) * 100.0
            / COUNT(*) DESC
    )                                           AS quarter_rank
FROM "surf_pipeline_db"."buoy_data_transforme