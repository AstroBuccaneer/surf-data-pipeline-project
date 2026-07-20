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

# NOAA NDBC API base URL
BASE_URL = "https://www.ndbc.noaa.gov/data/realtime2"

def fetch_wave_data(buoy_id, start_date, end_date):
    """Fetch historical wave data for a given NOAA buoy ID."""

    url = f"{BASE_URL}/{buoy_id}.txt"
    
    response = requests.get(url)

    if response.status_code == 200:
        print(f"✓ Raw data received for buoy {buoy_id}")
        return response.text
    else:
        print(f"Error fetching data for buoy {buoy_id}: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
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
    # Date range to pull
    start_date = "2020-01-01"
    end_date = "2023-12-31"

    print("Starting NOAA data extraction...")
    results = fetch_all_locations(start_date, end_date)

    # Save raw results to data/raw/
    output_path = "data/raw/noaa_wave_data.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\n✓ Raw data saved to {output_path}")
    print(f"✓ Locations retrieved: {list(results.keys())}")