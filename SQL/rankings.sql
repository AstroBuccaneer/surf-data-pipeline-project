-- ============================================
-- Surf Data Pipeline - Location Rankings
-- ============================================

-- 1. Overall max wave height per location with benchmark comparison
SELECT
    l.name                          AS location,
    MAX(w.wave_height_m)            AS max_wave_height_m,
    ROUND(MAX(w.wave_height_m) * 3.28084, 2) AS max_wave_height_ft,
    ROUND(MAX(w.benchmark_pct_nazare), 2)    AS pct_of_nazare,
    ROUND(MAX(w.benchmark_pct_lituya), 2)    AS pct_of_lituya
FROM wave_events w
JOIN dim_location l ON w.location_id = l.location_id
WHERE w.wave_height_m IS NOT NULL
GROUP BY l.name
ORDER BY max_wave_height_m DESC;


-- 2. Seasonal wave height rankings using window functions
SELECT
    l.name                              AS location,
    d.season,
    ROUND(AVG(w.wave_height_m), 2)      AS avg_wave_height_m,
    ROUND(MAX(w.wave_height_m), 2)      AS max_wave_height_m,
    COUNT(*)                            AS total_readings,
    RANK() OVER (
        PARTITION BY d.season
        ORDER BY AVG(w.wave_height_m) DESC
    )                                   AS season_rank
FROM wave_events w
JOIN dim_location l ON w.location_id = l.location_id
JOIN dim_date d ON w.date_id = d.date_id
WHERE w.wave_height_m IS NOT NULL
GROUP BY l.name, d.season
ORDER BY d.season, season_rank;


-- 3. Hurricane season vs non hurricane season comparison using CTE
WITH hurricane_season AS (
    SELECT
        l.name                          AS location,
        ROUND(AVG(w.wave_height_m), 2)  AS avg_wave_height_m,
        COUNT(*)                        AS total_readings
    FROM wave_events w
    JOIN dim_location l ON w.location_id = l.location_id
    JOIN dim_date d ON w.date_id = d.date_id
    WHERE d.is_hurricane_season = 'Yes'
    AND w.wave_height_m IS NOT NULL
    GROUP BY l.name
),
non_hurricane_season AS (
    SELECT
        l.name                          AS location,
        ROUND(AVG(w.wave_height_m), 2)  AS avg_wave_height_m,
        COUNT(*)                        AS total_readings
    FROM wave_events w
    JOIN dim_location l ON w.location_id = l.location_id
    JOIN dim_date d ON w.date_id = d.date_id
    WHERE d.is_hurricane_season = 'No'
    AND w.wave_height_m IS NOT NULL
    GROUP BY l.name
)
SELECT
    h.location,
    h.avg_wave_height_m                 AS hurricane_season_avg,
    n.avg_wave_height_m                 AS non_hurricane_season_avg,
    ROUND(h.avg_wave_height_m - 
          n.avg_wave_height_m, 2)       AS difference
FROM hurricane_season h
JOIN non_hurricane_season n ON h.location = n.location
ORDER BY difference DESC;


-- 4. Top 10 highest wave events ever recorded across all locations
SELECT
    l.name                              AS location,
    d.date                              AS date,
    d.season                            AS season,
    w.wave_height_m                     AS wave_height_m,
    ROUND(w.wave_height_m * 3.28084, 2) AS wave_height_ft,
    ROUND(w.benchmark_pct_nazare, 2)    AS pct_of_nazare,
    ROW_NUMBER() OVER (
        ORDER BY w.wave_height_m DESC
    )                                   AS overall_rank
FROM wave_events w
JOIN dim_location l ON w.location_id = l.location_id
JOIN dim_date d ON w.date_id = d.date_id
WHERE w.wave_height_m IS NOT NULL
LIMIT 10;