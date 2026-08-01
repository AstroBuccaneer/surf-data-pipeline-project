import pytest
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCleanedData:

    def test_buoy_data_exists(self):
        """Test cleaned buoy data file exists."""
        assert os.path.exists("data/processed/buoy_data_clean.csv")

    def test_storm_data_exists(self):
        """Test cleaned storm data file exists."""
        assert os.path.exists("data/processed/storm_data_clean.csv")

    def test_seismic_data_exists(self):
        """Test cleaned seismic data file exists."""
        assert os.path.exists("data/processed/seismic_data_clean.csv")

    def test_benchmarks_clean_exists(self):
        """Test cleaned benchmarks file exists."""
        assert os.path.exists("data/processed/benchmarks_clean.csv")

    def test_buoy_data_has_required_columns(self):
        """Test buoy data has all required columns."""
        df = pd.read_csv("data/processed/buoy_data_clean.csv")
        required_cols = ["location", "year", "month", "day",
                        "wave_height_m", "source"]
        for col in required_cols:
            assert col in df.columns

    def test_buoy_data_has_4_locations(self):
        """Test buoy data contains all 4 locations."""
        df = pd.read_csv("data/processed/buoy_data_clean.csv")
        locations = df["location"].unique()
        assert "pensacola_beach" in locations
        assert "cocoa_beach" in locations
        assert "waikiki" in locations
        assert "huntington_beach" in locations

    def test_buoy_wave_height_no_extreme_values(self):
        """Test wave heights are within realistic range."""
        df = pd.read_csv("data/processed/buoy_data_clean.csv")
        valid = df["wave_height_m"].dropna()
        assert valid.max() <= 30
        assert valid.min() >= 0

    def test_seismic_data_has_required_columns(self):
        """Test seismic data has all required columns."""
        df = pd.read_csv("data/processed/seismic_data_clean.csv")
        required_cols = ["location", "magnitude", "time", "source"]
        for col in required_cols:
            assert col in df.columns

    def test_seismic_magnitude_range(self):
        """Test seismic magnitudes are above minimum threshold."""
        df = pd.read_csv("data/processed/seismic_data_clean.csv")
        valid = df["magnitude"].dropna()
        assert valid.min() >= 4.0

    def test_benchmarks_has_2_records(self):
        """Test benchmarks file has exactly 2 records."""
        df = pd.read_csv("data/processed/benchmarks_clean.csv")
        assert len(df) == 2


class TestStarSchema:

    def test_database_exists(self):
        """Test SQLite database exists."""
        assert os.path.exists("data/final/surf_pipeline.db")

    def test_surf_scores_exists(self):
        """Test surf scores file exists."""
        assert os.path.exists("data/processed/surf_scores.csv")

    def test_surf_scores_has_4_locations(self):
        """Test surf scores has all 4 locations."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert len(df) == 4

    def test_surf_scores_rank_column_exists(self):
        """Test surf scores has rank column."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert "rank" in df.columns

    def test_surf_scores_in_valid_range(self):
        """Test surf scores are between 0 and 100."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert df["surf_potential_score"].min() >= 0
        assert df["surf_potential_score"].max() <= 100