# Data Model Documentation

## Overview
The surf pipeline uses a star schema with one fact table
and four dimension tables stored in SQLite locally and
queryable via Athena in the cloud.

## Star Schema Diagram

                    dim_date
                        │
dim_location ──── wave_events ──── dim_benchmark
                        │
                    dim_cause

## Fact Table — wave_events
| Column | Type | Description |
|---|---|---|
| location_id | INTEGER | FK to dim_location |
| date_id | INTEGER | FK to dim_date |
| year | INTEGER | Year of reading |
| month | INTEGER | Month of reading |
| wave_height_m | REAL | Wave height in meters |
| dominant_period_sec | REAL | Dominant wave period |
| wind_speed_ms | REAL | Wind speed m/s |
| benchmark_pct_nazare | REAL | % of Nazaré record |
| benchmark_pct_lituya | REAL | % of Lituya Bay record |
| source | TEXT | Data source identifier |

## Dimension Tables

### dim_location
| Column | Type | Description |
|---|---|---|
| location_id | INTEGER | Primary key |
| location_key | TEXT | Slug identifier |
| name | TEXT | Display name |
| state | TEXT | US state |
| lat | REAL | Latitude |
| lon | REAL | Longitude |
| noaa_buoy_id | TEXT | NOAA buoy identifier |
| primary_cause | TEXT | Primary wave cause type |
| region | TEXT | Ocean region |

### dim_cause
| Column | Type | Description |
|---|---|---|
| cause_id | INTEGER | Primary key |
| cause_key | TEXT | Slug identifier |
| cause_name | TEXT | Display name |
| cause_category | TEXT | meteorological/geological/oceanographic |
| surfable | TEXT | Yes/No |
| description | TEXT | Cause description |

### dim_date
| Column | Type | Description |
|---|---|---|
| date_id | INTEGER | Primary key (YYYYMMDD) |
| date | TEXT | Full date string |
| year | INTEGER | Year |
| month | INTEGER | Month number |
| month_name | TEXT | Month name |
| day | INTEGER | Day |
| quarter | INTEGER | Quarter 1-4 |
| season | TEXT | Winter/Spring/Summer/Fall |
| is_hurricane_season | TEXT | Yes/No |

### dim_benchmark
| Column | Type | Description |
|---|---|---|
| benchmark_id | INTEGER | Primary key |
| benchmark_key | TEXT | Slug identifier |
| name | TEXT | Benchmark name |
| location | TEXT | Where it occurred |
| year | INTEGER | Year it occurred |
| wave_height_ft | REAL | Height in feet |
| wave_height_m | REAL | Height in meters |
| cause | TEXT | What caused it |
| cause_type | TEXT | Cause category |
| surfable | TEXT | Yes/No |
| surfer | TEXT | Surfer name if applicable |

## Why Star Schema
- Simple and fast for analytical queries
- Easy to understand for non technical stakeholders
- Optimized for aggregations and GROUP BY queries
- Scales well to cloud data warehouses like Redshift and Athena
- Chosen over snowflake for query simplicity at this data size


