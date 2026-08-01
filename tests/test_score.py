import pytest
import pandas as pd
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSurfScore:

    def test_surf_scores_file_exists(self):
        """Test surf scores output file exists."""
        assert os.path.exists("data/processed/surf_scores.csv")

    def test_all_4_locations_scored(self):
        """Test all 4 locations have scores."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert len(df) == 4

    def test_scores_are_positive(self):
        """Test all surf scores are positive."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert (df["surf_potential_score"] > 0).all()

    def test_scores_under_100(self):
        """Test all surf scores are under 100."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert (df["surf_potential_score"] <= 100).all()

    def test_ranks_are_unique(self):
        """Test no two locations share the same rank."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert df["rank"].nunique() == 4

    def test_ranks_are_1_to_4(self):
        """Test ranks are 1 through 4."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert set(df["rank"].values) == {1, 2, 3, 4}

    def test_waikiki_is_top_ranked(self):
        """Test Waikiki is ranked number 1."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        top = df[df["rank"] == 1]["location_name"].values[0]
        assert top == "Waikiki"

    def test_pct_of_nazare_under_100(self):
        """Test no location exceeds Nazare benchmark."""
        df = pd.read_csv("data/processed/surf_scores.csv")
        assert (df["pct_of_nazare"] <= 100).all()


class TestStarSchemaQueries:

    def setup_method(self):
        """Connect to database before each test."""
        self.conn = sqlite3.connect("data/final/surf_pipeline.db")

    def teardown_method(self):
        """Close database after each test."""
        self.conn.close()

    def test_wave_events_table_exists(self):
        """Test wave_events fact table exists."""
        cursor = self.conn.cursor()
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        assert "wave_events" in table_names

    def test_dim_location_has_4_records(self):
        """Test dim_location has exactly 4 records."""
        cursor = self.conn.cursor()
        count = cursor.execute(
            "SELECT COUNT(*) FROM dim_location"
        ).fetchone()[0]
        assert count == 4

    def test_dim_benchmark_has_2_records(self):
        """Test dim_benchmark has exactly 2 records."""
        cursor = self.conn.cursor()
        count = cursor.execute(
            "SELECT COUNT(*) FROM dim_benchmark"
        ).fetchone()[0]
        assert count == 2

    def test_wave_events_has_records(self):
        """Test wave_events has data."""
        cursor = self.conn.cursor()
        count = cursor.execute(
            "SELECT COUNT(*) FROM wave_events"
        ).fetchone()[0]
        assert count > 0

    def test_benchmark_pct_nazare_not_null(self):
        """Test benchmark percentage column has values."""
        cursor = self.conn.cursor()
        count = cursor.execute(
            """SELECT COUNT(*) FROM wave_events
               WHERE benchmark_pct_nazare IS NOT NULL"""
        ).fetchone()[0]
        assert count > 0

    def test_all_locations_in_wave_events(self):
        """Test all 4 locations have wave events."""
        cursor = self.conn.cursor()
        count = cursor.execute(
            """SELECT COUNT(DISTINCT location_id)
               FROM wave_events"""
        ).fetchone()[0]
        assert count == 4


class TestMLOutputs:

    def test_model_exists(self):
        """Test trained model file exists."""
        assert os.path.exists("data/final/best_model.pkl")

    def test_model_metadata_exists(self):
        """Test model metadata file exists."""
        assert os.path.exists("data/final/model_metadata.json")

    def test_evaluation_report_exists(self):
        """Test evaluation report exists."""
        assert os.path.exists("data/final/evaluation_report.json")

    def test_predictions_exist(self):
        """Test surf predictions file exists."""
        assert os.path.exists("data/final/surf_predictions.json")

    def test_training_data_exists(self):
        """Test training data files exist."""
        assert os.path.exists("data/final/X_train.csv")
        assert os.path.exists("data/final/X_test.csv")
        assert os.path.exists("data/final/y_train.csv")
        assert os.path.exists("data/final/y_test.csv")