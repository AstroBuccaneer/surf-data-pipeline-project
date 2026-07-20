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