import json
import yaml
import os

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

def get_benchmarks():
    """Return hardcoded world record wave benchmarks."""

    benchmarks = {
        "lituya_bay": {
            "name": "Lituya Bay Megatsunami",
            "location": "Lituya Bay, Alaska",
            "year": 1958,
            "wave_height_ft": 1720,
            "wave_height_m": 524,
            "cause": "Landslide triggered by magnitude 7.8 earthquake",
            "cause_type": "seismic",
            "surfable": "No",
            "notes": "Largest wave ever recorded. Not surfable — scientific upper bound only."
        },
        "nazare": {
            "name": "Nazaré Big Wave Record",
            "location": "Nazaré, Portugal",
            "year": 2020,
            "wave_height_ft": 86,
            "wave_height_m": 26.2,
            "cause": "Underwater canyon amplifying Atlantic swell",
            "cause_type": "swell_amplification",
            "surfer": "Sebastian Steudtner",
            "surfable": "Yes",
            "notes": "Largest wave ever surfed. Human surfability ceiling for scoring."
        }
    }

    return benchmarks

if __name__ == "__main__":
    print("Loading benchmark reference data...")
    
    benchmarks = get_benchmarks()

    # Save to data/raw/
    output_path = "data/raw/benchmarks.json"
    with open(output_path, "w") as f:
        json.dump(benchmarks, f, indent=4)

    print(f"\n✓ Benchmarks saved to {output_path}")
    print(f"\n--- Benchmark Summary ---")
    for key, b in benchmarks.items():
        print(f"\n{b['name']}")
        print(f"  Location : {b['location']}")
        print(f"  Year     : {b['year']}")
        print(f"  Height   : {b['wave_height_ft']} ft / {b['wave_height_m']} m")
        print(f"  Cause    : {b['cause']}")
        print(f"  Surfable : {b['surfable']}")