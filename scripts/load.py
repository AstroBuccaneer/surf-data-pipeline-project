import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from load.s3_loader import upload_raw_data, upload_processed_data, upload_final_data
import boto3
import yaml

def run_load():
    """Run full load pipeline."""

    print("=" * 60)
    print("SURF PIPELINE — LOAD PHASE")
    print("=" * 60)

    # Load config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Upload raw data
    print("\n[1/3] Uploading raw data to S3...")
    upload_raw_data()
    print("✓ Raw data uploaded")

    # Upload processed data
    print("\n[2/3] Uploading processed data to S3...")
    upload_processed_data()
    print("✓ Processed data uploaded")

    # Upload final data
    print("\n[3/3] Uploading final data to S3...")
    upload_final_data()
    print("✓ Final data uploaded")

    # Verify uploads
    print("\nVerifying S3 uploads...")
    s3 = boto3.client("s3", region_name=config["aws"]["region"])

    for bucket in [
        config["aws"]["s3_bucket_raw"],
        config["aws"]["s3_bucket_processed"],
        config["aws"]["s3_bucket_final"]
    ]:
        response = s3.list_objects_v2(Bucket=bucket)
        count = response.get("KeyCount", 0)
        print(f"✓ s3://{bucket} : {count} files")

    print("\n" + "=" * 60)
    print("✓ LOAD PHASE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_load()