-- ============================================
-- Surf Data Pipeline - Deep Analysis
-- ============================================

-- 1. Year over year wave height trend per location using window functions
WITH yearly_avg AS (
    SELECT
        l.name                              AS location,
        w.year,
        ROUND(AVG(w.wave_height_m), 2)      AS avg_wave_height_m
    FROM wave_events w
    JOIN dim_location l ON w.location_id = l.location_id
    WHERE w.wave_height_m IS NOT NULL
    GROUP BY l.name, w.year
)
SELECT
    location,
    year,
    avg_wave_height_m,
    ROUND(AVG(avg_wave_height_m) OVER (
        PARTITION BY location
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                                   AS rolling_3yr_avg,
    RANK() OVER (
        PARTITION BY location
        ORDER BY avg_wave_height_m DESC
    )                                       AS year_rank
FROM yearly_avg
ORDER BY location, year;


-- 2. Best month to surf at each location
WITH monthly_avg AS (
    SELECT
        l.name                              AS location,
        d.month_name,
        d.month,
        ROUND(AVG(w.wave_height_m), 2)      AS avg_wave_height_m,
        SUM(CASE WHEN w.wave_height_m >= 1.5 
            THEN 1 ELSE 0 END)              AS surfable_days,
        COUNT(*)                            AS total_readings
    FROM wave_events w
    JOIN dim_location l ON w.location_id = l.location_id
    JOIN dim_date d ON w.date_id = d.date_id
    WHERE w.wave_height_m IS NOT NULL
    GROUP BY l.name, d.month_name, d.month
)
SELECT
    location,
    month_name,
    avg_wave_height_m,
    surfable_days,
    RANK() OVER (
        PARTITION BY location
        ORDER BY avg_wave_height_m DESC
    )                                       AS best_month_rank
FROM monthly_avg
ORDER BY location, best_month_rank;


-- 3. How close has each location ever gotten to the Nazare benchmark
WITH nazare_comparison AS (
    SELECT
        l.name                              AS location,
        MAX(w.benchmark_pct_nazare)         AS closest_pct_to_nazare,
        MAX(w.wave_height_m)                AS max_wave_m,
        ROUND(MAX(w.wave_height_m) 
            * 3.28084, 2)                   AS max_wave_ft,
        26.2 - MAX(w.wave_height_m)         AS gap_to_nazare_m
    FROM wave_events w
    JOIN dim_location l ON w.location_id = l.location_id
    WHERE w.wave_height_m IS NOT NULL
    GROUP BY l.name
)
SELECT
    location,
    max_wave_ft,
    ROUND(closest_pct_to_nazare, 2)         AS pct_of_nazare,
    ROUND(gap_to_nazare_m, 2)               AS gap_to_nazare_m,
    ROUND(gap_to_nazare_m * 3.28084, 2)     AS gap_to_nazare_ft,
    RANK() OVER (
        ORDER BY closest_pct_to_nazare DESC
    )                                       AS nazare_rank
FROM nazare_comparison
ORDER BY nazare_rank;


-- 4. Surfable wave frequency by quarter and location
SELECT
    l.name                                  AS location,
    d.quarter,
    COUNT(*)                                AS total_readings,
    SUM(CASE WHEN w.wave_height_m >= 1.5 
        THEN 1 ELSE 0 END)                  AS surfable_readings,
    ROUND(SUM(CASE WHEN w.wave_height_m >= 1.5
        THEN 1 ELSE 0 END) * 100.0 
        / COUNT(*), 2)                      AS surfable_pct,
    RANK() OVER (
        PARTITION BY d.quarter
        ORDER BY SUM(CASE WHEN w.wave_height_m >= 1.5
            THEN 1 ELSE 0 END) * 100.0 
            / COUNT(*) DESC
    )                                       AS quarter_rank
FROM wave_events w
JOIN dim_location l ON w.location_id = l.location_id
JOIN dim_date d ON w.date_id = d.date_id
WHERE w.wave_height_m IS NOT NULL
GROUP BY l.name, d.quarter
ORDER BY d.quarter, quarter_rank;