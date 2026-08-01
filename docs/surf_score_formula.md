# Surf Score Formula Documentation

## Overview
The surf potential index scores each location on a 0-100 scale
using three weighted components compared against two world record
benchmarks.

## Benchmarks

### Scientific Upper Bound — Lituya Bay 1958
- Wave height: 1,720 ft (524m)
- Cause: Magnitude 7.8 earthquake triggering rockslide
- Surfable: No
- Purpose: Absolute upper bound reference only

### Human Surfability Ceiling — Nazaré 2020
- Wave height: 86 ft (26.2m)
- Cause: Underwater canyon amplifying Atlantic swells
- Surfer: Sebastian Steudtner
- Surfable: Yes
- Purpose: Primary scoring ceiling — 100% benchmark

## Formula
surf_potential_score = (
(peak_score * 0.50) +
(surfable_pct * 0.30) +
(seismic_score * 0.20)
)

## Components

### 1. Peak Magnitude Score (50% weight)
Measures how close the location's highest recorded wave
gets to the Nazaré benchmark.

peak_score = (max_wave_height_m / 26.2) * 100

### 2. Surfable Frequency Score (30% weight)
Percentage of buoy readings where wave height >= 1.5m
(approximately 5 feet — minimum surfable height).

surfable_pct = (surfable_readings / total_readings) * 100

### 3. Seismic Recurrence Score (20% weight)
Normalized score based on number of magnitude 4.0+
earthquake events within 500km of each location.

seismic_score = (location_events / max_events_any_location) * 100

## Results

| Rank | Location | Peak Score | Surfable % | Seismic Score | Final Score |
|---|---|---|---|---|---|
| 1 | Waikiki | 34.69 | 48.87 | 30.48 | 67.41 |
| 2 | Huntington Beach | 24.24 | 40.69 | 100.00 | 64.81 |
| 3 | Cocoa Beach | 37.18 | 23.70 | 0.12 | 57.13 |
| 4 | Pensacola Beach | 35.73 | 17.60 | 0.72 | 53.47 |

## Key Insights
- Waikiki wins on consistent Pacific swell frequency
- Huntington Beach has dominant seismic activity (830 events)
- Cocoa Beach has highest single wave but low frequency
- Pensacola Beach hurt by low surfable frequency despite decent peaks

## Design Decisions
- Nazaré chosen as ceiling because it represents maximum human
  surfability — Lituya Bay is scientifically interesting but
  not relevant to actual surf potential
- 1.5m minimum surfable threshold based on standard surf industry
  definition of rideable waves
- 500km seismic radius wide enough to capture offshore events
  that generate tsunami or swell toward each location
- Weights configurable in config.yaml for easy adjustment

## Future Improvements
- Add tidal data as additional scoring component
- Weight hurricane season events more heavily for Florida locations
- Add bathymetry score — underwater terrain affects wave quality
- Incorporate WSL historical event data for verified big wave records

