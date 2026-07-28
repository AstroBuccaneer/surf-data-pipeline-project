-- ============================================
-- Surf Data Pipeline - Table Definitions
-- ============================================

-- Location Dimension
CREATE TABLE IF NOT EXISTS dim_location (
    location_id     INTEGER PRIMARY KEY,
    location_key    TEXT,
    name            TEXT,
    state           TEXT,
    lat             REAL,
    lon             REAL,
    noaa_buoy_id    TEXT,
    primary_cause   TEXT,
    region          TEXT
);

-- Cause Dimension
CREATE TABLE IF NOT EXISTS dim_cause (
    cause_id        INTEGER PRIMARY KEY,
    cause_key       TEXT,
    cause_name      TEXT,
    cause_category  TEXT,
    surfable        TEXT,
    description     TEXT
);

-- Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_id             INTEGER PRIMARY KEY,
    date                TEXT,
    year                INTEGER,
    month               INTEGER,
    month_name          TEXT,
    day                 INTEGER,
    quarter             INTEGER,
    season              TEXT,
    is_hurricane_season TEXT
);

-- Benchmark Dimension
CREATE TABLE IF NOT EXISTS dim_benchmark (
    benchmark_id    INTEGER PRIMARY KEY,
    benchmark_key   TEXT,
    name            TEXT,
    location        TEXT,
    year            INTEGER,
    wave_height_ft  REAL,
    wave_height_m   REAL,
    cause           TEXT,
    cause_type      TEXT,
    surfable        TEXT,
    surfer          TEXT,
    notes           TEXT
);

-- Wave Events Fact Table
CREATE TABLE IF NOT EXISTS wave_events (
    event_id                INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id             INTEGER,
    date_id                 INTEGER,
    year                    INTEGER,
    month                   INTEGER,
    wave_height_m           REAL,
    dominant_period_sec     REAL,
    wind_speed_ms           REAL,
    benchmark_pct_nazare    REAL,
    benchmark_pct_lituya    REAL,
    source                  TEXT,
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);