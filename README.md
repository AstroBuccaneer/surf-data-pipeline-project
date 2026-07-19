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

### Day 3 — 