# Surf Data Pipeline 🌊

## Project Overview
A production-grade data pipeline comparing surf potential across 4 locations —
Pensacola Beach, Cocoa Beach, Waikiki, and Huntington Beach — scored against
two world record benchmarks:
- **Lituya Bay, Alaska (1958)** — largest wave ever recorded (~1,720 ft)
- **Nazaré, Portugal (2020)** — largest wave ever surfed (~86 ft) by Sebastian Steudtner

## The So What
A data-driven answer to where and when to chase the best waves — backed by 
historical weather data, seismic records, and machine learning predictions.
Built as a production pipeline covering data engineering, AWS, and ML.

## Tech Stack
- Python, Pandas, PySpark, SQL, SQLite
- Apache Airflow
- AWS (S3, Glue, Athena, Lambda, Kinesis, SageMaker, Bedrock)
- CloudFormation

## Data Model
- Star schema with fact table `wave_events` and dimensions for location, cause, date, and benchmark

## Project Build Log

### Day 1 
- Created full project folder structure across all 4 phases
- Initialized GitHub repository and pushed initial structure

### Day 2
- Created `config.yaml` as the central source of truth for the entire pipeline
- Configured all 4 surf locations (Pensacola Beach, Cocoa Beach, Waikiki, 
  Huntington Beach) with coordinates and NOAA buoy IDs
- Added both world record benchmarks (Lituya Bay 1720ft, Nazaré 86ft) 
  with cause metadata and surfability flags
- Set up scoring weights for surf potential index
- Configured data paths and AWS placeholders for future phases
- Created `.env` file locally to store API keys securely (not pushed to GitHub)
- Created `.gitignore` to protect sensitive files, API keys, and data folders
  from being pushed to GitHub
- Registered for NOAA API token for Day 3 data extraction

### Day 3
- Built `extract/noaa_buoy.py` to pull live NOAA NDBC buoy data
- Successfully pulling real wave height, swell, and wind data for all 4 locations
- Raw data saved to `data/raw/noaa_wave_data.json`

**Debugging Notes:**
- Initially used NOAA CDO API with `LOCAL_CLIMATOLOGICAL_DATA` → got 500 error
  (wrong API for ocean buoy data)
- Switched to NOAA CO-OPS API with `waves` product → got 400 error
  (CO-OPS doesn't support wave height as a product)
- Switched to NOAA NDBC (National Data Buoy Center) → success
  (NDBC is the correct source for ocean buoy wave height, swell period, and wind speed)

  ### Day 4
- Built `extract/noaa_storms.py` to pull NOAA Storm Events data for all 4 locations
- Debugged Storm Events API — switched to direct CSV file downloads
- Built directory listing scraper to find exact filenames dynamically
- Added idempotency checkpoint system — saves each year individually so 
  pipeline resumes where it left off if connection drops
- Lost connection mid-run on Huntington Beach 2005, restarted and checkpoint 
  system skipped already completed Florida files automatically
- Successfully pulled storm data 2000-2023 for Florida, Hawaii, and California

**Debugging Notes:**
- ChunkedEncodingError caused by unstable network dropping mid-download
- Fixed with idempotency checkpoint pattern — production standard for 
  long running network dependent pipelines

  ### Day 5
- Built `extract/usgs_seismic.py` to pull USGS earthquake data for all 4 locations
- Used lat/lon coordinates from config.yaml to search within 500km radius
- Filtered to magnitude 4.0+ events ordered by magnitude
- Results already showing story: Huntington Beach (830) and Waikiki (253) 
  have far more seismic activity than Pensacola (6) and Cocoa Beach (1)
- Seismic frequency feeds directly into surf score causative factor weighting

**Design Decisions:**
- `radius_km=500` — wide enough to catch offshore seismic events that 
  could generate waves toward each location
- `minmagnitude=4.0` — filters out small earthquakes that wouldn't affect 
  wave conditions
- `orderby=magnitude` — returns the biggest events first which is perfect 
  for benchmark comparison against Lituya Bay's 7.8 magnitude trigger

  ### Day 6
- Built `extract/benchmarks.py` with hardcoded world record reference data
- Lituya Bay 1958 — 1720ft megatsunami, seismic cause, not surfable (upper bound)
- Nazaré 2020 — 86ft by Sebastian Steudtner, swell amplification cause, surfable (scoring ceiling)
- Benchmarks saved to `data/raw/benchmarks.json`

**Design Decision:**
- Lituya Bay hardcoded permanently — geological event that will never change
- Nazaré treated as dynamic in future — WSL records could be broken and 
  would need automatic updating via Airflow DAG in Phase 3


  ### Day 7
- Built `transform/clean.py` to normalize all raw data sources
- Parsed NOAA NDBC text format into structured records
- Handled missing values marked as `MM` converting to null
- Standardized column names across all 4 locations
- Results: 21,462 buoy records, 130,012 storm records, 
  1,090 seismic records, 2 benchmarks
- All cleaned data saved to `data/processed/`

**Design Decisions:**
- Parsed raw NOAA NDBC text format into structured records
- Handled missing values marked as `MM` by converting to None/null
- Standardized column names across all 4 locations
- Wave height kept in meters for consistency
- Saved as CSV for easy loading into star schema

### Day 8
- Built `transform/schema.py` to create star schema in SQLite
- dim_location: 4 surf locations with coordinates and buoy IDs
- dim_cause: 5 cause types (hurricane, tropical storm, pacific swell, seismic, swell amplification)
- dim_date: 8,766 days from 2000-2023 tagged with season and hurricane season flag
- dim_benchmark: 2 world records (Lituya Bay and Nazaré)
- wave_events: 21,462 fact records with benchmark percentage scores vs Nazaré and Lituya Bay
- Star schema saved to data/final/surf_pipeline.db

**Design Decisions:**
- Every buoy reading scored as percentage of both benchmarks directly in fact table
- Date dimension includes hurricane season flag for seasonal surf analysis
- Star schema chosen over snowflake for simplicity and query performance

### Day 9
- Built `transform/score.py` to calculate surf potential index
- Three scoring components:
  - Peak magnitude score (50% weight) — max wave height vs Nazaré benchmark
  - Surfable frequency score (30% weight) — % of readings above 1.5m
  - Seismic recurrence score (20% weight) — earthquake frequency and severity
- Final Rankings:
  1. Huntington Beach — 81.91
  2. Waikiki — 55.44
  3. Pensacola Beach — 46.51
  4. Cocoa Beach — 41.05
- Scores saved to data/processed/surf_scores.csv

**Key Insights:**
- Huntington Beach wins due to 830 seismic events and 39.71% surfable frequency
- Waikiki strong due to consistent Pacific swells and 253 seismic events
- Pensacola hurt by low frequency despite recording second highest single wave
- Cocoa Beach most sheltered — only 1 seismic event and 2% surfable frequency


### Day 10
- Built `sql/create_tables.sql` — star schema DDL definitions
- Built `sql/rankings.sql` — location rankings using joins, window functions, CTEs
- Built `sql/analysis.sql` — deep analysis including year over year trends, 
  best month to surf, Nazaré gap analysis, and quarterly rankings
- SQL files ready to run against SQLite locally and Athena in Phase 3

**SQL Concepts Covered:**
- Joins (fact to dimension tables)
- CTEs (hurricane season comparison)
- Window functions (RANK, ROW_NUMBER, rolling averages)
- Aggregations (GROUP BY, HAVING)
- Conditional aggregations (CASE WHEN)


### Day 11
- Built `spark/pyspark_transform.py` to reprocess data at scale with PySpark
- Fixed Java version error — upgraded from Java 8 to Java 17
- Successfully loaded 21,462 buoy, 130,012 storm, 1,090 seismic records into Spark
- PySpark transformations mirror pandas version confirming data consistency
- Results saved to data/final/

**PySpark vs Pandas:**
- F.when() is equivalent to CASE WHEN in SQL
- Window.partitionBy() is equivalent to PARTITION BY in SQL
- F.rank().over(window) is your window function in Python
- spark.sql.shuffle.partitions set to 4 for small local dataset

**Debugging Notes:**
- Java UnsupportedClassVersionError — PySpark requires Java 17+
- Fixed by downloading Java 17 and setting JAVA_HOME environment variable
- PyArrow warning is non-critical — Spark fell back to non-optimized conversion


### Day 12
- Built `dags/surf_pipeline_dag.py` — Airflow DAG orchestrating full pipeline
- 7 tasks defined across extract and transform phases
- All 4 extract tasks run in parallel, then clean, schema, score run in sequence
- Scheduled to run every Monday at 6am via cron expression
- DAG ready to deploy to AWS MWAA in Phase 3

**DAG Design Decisions:**
- retries: 2 — automatically retries failed tasks twice before giving up
- retry_delay: 5 minutes — waits between retries
- schedule_interval: 0 6 * * 1 — cron for every Monday at 6am
- catchup=False — don't backfill missed runs if pipeline was down
- Parallel extract tasks reduce total pipeline runtime significantly

**What is a DAG:**
Directed Acyclic Graph — Airflow's blueprint for pipeline orchestration.
Defines tasks, dependencies, and schedule so pipeline runs automatically
without manual intervention.