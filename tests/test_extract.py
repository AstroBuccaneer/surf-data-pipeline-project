import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract.benchmarks import get_benchmarks
from extract.usgs_seismic import fetch_seismic_data

class TestBenchmarks:

    def test_benchmarks_returns_two_records(self):
        """Test that benchmarks returns exactly 2 records."""
        benchmarks = get_benchmarks()
        assert len(benchmarks) == 2

    def test_lituya_bay_height(self):
        """Test Lituya Bay wave height is correct."""
        benchmarks = get_benchmarks()
        assert benchmarks["lituya_bay"]["wave_height_ft"] == 1720

    def test_nazare_height(self):
        """Test Nazaré wave height is correct."""
        benchmarks = get_benchmarks()
        assert benchmarks["nazare"]["wave_height_m"] == 26.2

    def test_nazare_is_surfable(self):
        """Test Nazaré is marked as surfable."""
        benchmarks = get_benchmarks()
        assert benchmarks["nazare"]["surfable"] == "Yes"

    def test_lituya_not_surfable(self):
        """Test Lituya Bay is marked as not surfable."""
        benchmarks = get_benchmarks()
        assert benchmarks["lituya_bay"]["surfable"] == "No"

    def test_benchmark_keys_exist(self):
        """Test required keys exist in benchmark data."""
        benchmarks = get_benchmarks()
        required_keys = ["name", "location", "year", "wave_height_ft",
                        "wave_height_m", "cause", "surfable"]
        for key in required_keys:
            assert key in benchmarks["lituya_bay"]
            assert key in benchmarks["nazare"]


class TestRawDataFiles:

    def test_noaa_wave_data_exists(self):
        """Test raw buoy data file exists."""
        assert os.path.exists("data/raw/noaa_wave_data.json")

    def test_noaa_storm_data_exists(self):
        """Test raw storm data file exists."""
        assert os.path.exists("data/raw/noaa_storm_data.json")

    def test_usgs_seismic_data_exists(self):
        """Test raw seismic data file exists."""
        assert os.path.exists("data/raw/usgs_seismic_data.json")

    def test_benchmarks_data_exists(self):
        """Test raw benchmarks file exists."""
        assert os.path.exists("data/raw/benchmarks.json")

    def test_noaa_wave_data_has_4_locations(self):
        """Test buoy data contains all 4 locations."""
        with open("data/raw/noaa_wave_data.json", "r") as f:
            data = json.load(f)
        assert len(data) == 4
        assert "pensacola_beach" in data
        assert "cocoa_beach" in data
        assert "waikiki" in data
        assert "huntington_beach" in data