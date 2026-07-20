import requests
import yaml
import os
import gzip
import io
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# NOAA Storm Events API base URL
BASE_URL = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"

def fetch_storm_data(state_name, start_year, end_year):
    """Fetch historical storm events by downloading NOAA CSV files by year."""

    import os
    all_data = []

    # Create checkpoint folder if it doesn't exist
    checkpoint_dir = "data/raw/storms"
    os.makedirs(checkpoint_dir, exist_ok=True)

    # Get directory listing to find exact filenames
    dir_response = requests.get(BASE_URL)
    if dir_response.status_code != 200:
        print("Could not access NOAA storm events directory")
        return all_data

    for year in range(int(start_year), int(end_year) + 1):
        checkpoint_file = f"{checkpoint_dir}/{state_name}_{year}.json"

        # Skip if already downloaded
        if os.path.exists(checkpoint_file):
            print(f"✓ Skipping {state_name} {year} - already downloaded")
            with open(checkpoint_file, "r") as f:
                all_data.extend(json.load(f))
            continue

        # Find exact filename for this year
        search_str = f"StormEvents_details-ftp_v1.0_d{year}_"
        lines = dir_response.text.split("\n")
        filename = None

        for line in lines:
            if search_str in line:
                start = line.find(search_str)
                end = line.find(".csv.gz", start) + 7
                filename = line[start:end]
                break

        if not filename:
            print(f"✗ No file found for year {year}")
            continue

        url = f"{BASE_URL}{filename}"
        response = requests.get(url)

        if response.status_code == 200:
            year_data = []
            with gzip.open(io.BytesIO(response.content), 'rt') as f:
                for line in f:
                    if state_name.upper() in line.upper():
                        year_data.append(line.strip())

            # Save checkpoint for this year
            with open(checkpoint_file, "w") as f:
                json.dump(year_data, f)

            all_data.extend(year_data)
            print(f"✓ Got storm data for {state_name} - {year}")
        else:
            print(f"✗ Could not download file for year {year}")

    return all_data
    
def fetch_all_storm_data(start_year, end_year):
    """Fetch storm data for all locations in config."""

    state_fips = {
        "pensacola_beach": "FLORIDA",
        "cocoa_beach": "FLORIDA",
        "waikiki": "HAWAII",
        "huntington_beach": "CALIFORNIA"
    }

    results = {}

    for location_key, location_data in config["locations"].items():
        print(f"Fetching storm data for {location_data['name']}...")

        state = state_fips[location_key]
        data = fetch_storm_data(state, start_year, end_year)

        if data:
            results[location_key] = data
            print(f"✓ Got storm data for {location_data['name']}")
        else:
            print(f"✗ No storm data for {location_data['name']}")

    return results

if __name__ == "__main__":
    # Year range to pull
    start_year = "2000"
    end_year = "2023"

    print("Starting NOAA storm data extraction...")
    results = fetch_all_storm_data(start_year, end_year)

    # Save raw results to data/raw/
    output_path = "data/raw/noaa_storm_data.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\n✓ Raw storm data saved to {output_path}")
    print(f"✓ Locations retrieved: {list(results.keys())}")