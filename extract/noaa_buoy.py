import requests
import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Get NOAA token from .env
NOAA_TOKEN = os.getenv("NOAA_TOKEN")

# NOAA NDBC Historical Data
BASE_URL = "https://www.ndbc.noaa.gov/view_text_file.php"

def fetch_wave_data(buoy_id, start_date, end_date):
    """Fetch historical wave data for a given NOAA buoy ID."""

    all_data = []

    # Pull data year by year
    start_year = int(start_date[:4])
    end_year = int(end_date[:4])

    for year in range(start_year, end_year + 1):
        url = f"https://www.ndbc.noaa.gov/view_text_file.php?filename={buoy_id}h{year}.txt.gz&dir=data/historical/stdmet/"
        response = requests.get(url)

        if response.status_code == 200:
            print(f"✓ Got historical data for buoy {buoy_id} - {year}")
            all_data.append(response.text)
        else:
            print(f"✗ No historical data for buoy {buoy_id} - {year}")

    return "\n".join(all_data) if all_data else None
    
def fetch_all_locations(start_date, end_date):
    """Fetch wave data for all locations in config."""
    
    results = {}

    for location_key, location_data in config["locations"].items():
        print(f"Fetching data for {location_data['name']}...")
        
        buoy_id = location_data["noaa_buoy_id"]
        data = fetch_wave_data(buoy_id, start_date, end_date)
        
        if data:
            results[location_key] = data
            print(f"✓ Got data for {location_data['name']}")
        else:
            print(f"✗ No data for {location_data['name']}")

    return results


import json

if __name__ == "__main__":
    start_date = "2010-01-01"
    end_date = "2023-12-31"

    print("Starting NOAA data extraction...")
    results = fetch_all_locations(start_date, end_date)

    # Save raw results to data/raw/
    output_path = "data/raw/noaa_wave_data.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\n✓ Raw data saved to {output_path}")
    print(f"✓ Locations retrieved: {list(results.keys())}")