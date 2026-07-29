import boto3
import os
import yaml

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# S3 client
s3 = boto3.client("s3", region_name=config["aws"]["region"])

# Bucket names
RAW_BUCKET = config["aws"]["s3_bucket_raw"]
PROCESSED_BUCKET = config["aws"]["s3_bucket_processed"]
FINAL_BUCKET = config["aws"]["s3_bucket_final"]

print("✓ S3 client connected")


def upload_raw_data():
    """Upload raw data files to S3 raw bucket."""

    print("\nUploading raw data to S3...")

    raw_files = [
        "data/raw/noaa_wave_data.json",
        "data/raw/noaa_storm_data.json",
        "data/raw/usgs_seismic_data.json",
        "data/raw/benchmarks.json"
    ]

    for file_path in raw_files:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            s3.upload_file(
                file_path,
                RAW_BUCKET,
                f"raw/{file_name}"
            )
            print(f"✓ Uploaded {file_name} to s3://{RAW_BUCKET}/raw/")
        else:
            print(f"✗ File not found: {file_path}")


def upload_processed_data():
    """Upload processed CSV files to S3 processed bucket."""

    print("\nUploading processed data to S3...")

    processed_files = [
        "data/processed/buoy_data_clean.csv",
        "data/processed/storm_data_clean.csv",
        "data/processed/seismic_data_clean.csv",
        "data/processed/benchmarks_clean.csv",
        "data/processed/surf_scores.csv"
    ]

    for file_path in processed_files:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            s3.upload_file(
                file_path,
                PROCESSED_BUCKET,
                f"processed/{file_name}"
            )
            print(f"✓ Uploaded {file_name} to s3://{PROCESSED_BUCKET}/processed/")
        else:
            print(f"✗ File not found: {file_path}")


def upload_final_data():
    """Upload final data files to S3 final bucket."""

    print("\nUploading final data to S3...")

    final_files = [
        "data/final/spark_buoy_transformed.csv",
        "data/final/spark_location_summary.csv"
    ]

    for file_path in final_files:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            s3.upload_file(
                file_path,
                FINAL_BUCKET,
                f"final/{file_name}"
            )
            print(f"✓ Uploaded {file_name} to s3://{FINAL_BUCKET}/final/")
        else:
            print(f"✗ File not found: {file_path}")


if __name__ == "__main__":
    print("Starting S3 upload pipeline...\n")

    upload_raw_data()
    upload_processed_data()
    upload_final_data()

    # Verify uploads by listing S3 buckets
    print("\n--- S3 Upload Summary ---")
    
    for bucket in [RAW_BUCKET, PROCESSED_BUCKET, FINAL_BUCKET]:
        response = s3.list_objects_v2(Bucket=bucket)
        count = response.get("KeyCount", 0)
        print(f"s3://{bucket} : {count} files")

    print("\n✓ All data uploaded to S3!")