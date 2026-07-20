import requests
import yaml
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# USGS Earthquake API base URL
BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

def fetch_seismic_data(location_name, lat, lon, start_date, end_date, radius_km=500):
    """Fetch historical earthquake data near a given location."""

    params = {
        "format": "geojson",
        "starttime": start_date,
        "endtime": end_date,
        "latitude": lat,
        "longitude": lon,
        "maxradiuskm": radius_km,
        "minmagnitude": 4.0,
        "orderby": "magnitude"
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        count = data["metadata"]["count"]
        print(f"✓ Found {count} seismic events near {location_name}")
        return data
    else:
        print(f"Error fetching seismic data for {location_name}: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
def fetch_all_seismic_data(start_date, end_date):
    """Fetch seismic data for all locations in config."""

    results = {}

    for location_key, location_data in config["locations"].items():
        print(f"Fetching seismic data for {location_data['name']}...")

        lat = location_data["lat"]
        lon = location_data["lon"]

        data = fetch_seismic_data(
            location_data["name"],
            lat,
            lon,
            start_date,
            end_date
        )

        if data:
            results[location_key] = data
            print(f"✓ Got seismic data for {location_data['name']}")
        else:
            print(f"✗ No seismic data for {location_data['name']}")

    return results

if __name__ == "__main__":
    # Date range to pull
    start_date = "2000-01-01"
    end_date = "2023-12-31"

    print("Starting USGS seismic data extraction...")
    results = fetch_all_seismic_data(start_date, end_date)

    # Save raw results to data/raw/
    output_path = "data/raw/usgs_seismic_data.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\n✓ Raw seismic data saved to {output_path}")
    print(f"✓ Locations retrieved: {list(results.keys())}")