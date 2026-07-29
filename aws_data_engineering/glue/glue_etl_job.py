import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
import boto3

# Initialize Glue context
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

print("✓ Glue job initialized")


# S3 bucket names
RAW_BUCKET = "surf-pipeline-raw-agl"
PROCESSED_BUCKET = "surf-pipeline-processed-agl"
FINAL_BUCKET = "surf-pipeline-final-agl"

def read_raw_data():
    """Read raw data files from S3 into Glue DynamicFrames."""

    print("Reading raw data from S3...")

    # Read buoy data
    buoy_dyf = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [f"s3://{RAW_BUCKET}/raw/noaa_wave_data.json"]
        },
        format="json"
    )

    # Read seismic data
    seismic_dyf = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [f"s3://{RAW_BUCKET}/raw/usgs_seismic_data.json"]
        },
        format="json"
    )

    # Read benchmarks
    benchmark_dyf = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [f"s3://{RAW_BUCKET}/raw/benchmarks.json"]
        },
        format="json"
    )

    print(f"✓ Buoy records     : {buoy_dyf.count()}")
    print(f"✓ Seismic records  : {seismic_dyf.count()}")
    print(f"✓ Benchmarks       : {benchmark_dyf.count()}")

    return buoy_dyf, seismic_dyf, benchmark_dyf

def transform_buoy_data(buoy_dyf):
    """Transform buoy data using Glue and Spark."""

    print("\nTransforming buoy data...")

    # Convert DynamicFrame to Spark DataFrame for transformations
    buoy_df = buoy_dyf.toDF()

    # Filter nulls
    buoy_df = buoy_df.filter(F.col("wave_height_m").isNotNull())

    # Add wave height in feet
    buoy_df = buoy_df.withColumn(
        "wave_height_ft",
        F.round(F.col("wave_height_m") * 3.28084, 2)
    )

    # Add benchmark percentages
    buoy_df = buoy_df.withColumn(
        "pct_of_nazare",
        F.round(F.col("wave_height_m") / 26.2 * 100, 2)
    )

    buoy_df = buoy_df.withColumn(
        "pct_of_lituya",
        F.round(F.col("wave_height_m") / 524 * 100, 2)
    )

    # Add surfable flag
    buoy_df = buoy_df.withColumn(
        "is_surfable",
        F.when(F.col("wave_height_m") >= 1.5, "Yes").otherwise("No")
    )

    # Convert back to DynamicFrame
    transformed_dyf = DynamicFrame.fromDF(buoy_df, glueContext, "transformed_buoy")

    print(f"✓ Transformed {transformed_dyf.count()} buoy records")
    return transformed_dyf


def write_to_s3(dyf, bucket, prefix, format="csv"):
    """Write transformed data to S3."""

    print(f"\nWriting to s3://{bucket}/{prefix}...")

    glueContext.write_dynamic_frame.from_options(
        frame=dyf,
        connection_type="s3",
        connection_options={
            "path": f"s3://{bucket}/{prefix}",
            "partitionKeys": ["location"]
        },
        format=format,
        format_options={
            "writeHeader": True,
            "separator": ","
        }
    )

    print(f"✓ Data written to s3://{bucket}/{prefix}")


def write_to_glue_catalog(dyf, database, table_name):
    """Write transformed data to Glue Data Catalog."""

    print(f"\nWriting to Glue catalog: {database}.{table_name}...")

    glueContext.write_dynamic_frame.from_catalog(
        frame=dyf,
        database=database,
        table_name=table_name
    )

    print(f"✓ Data written to Glue catalog: {database}.{table_name}")


if __name__ == "__main__":
    print("Starting Glue ETL job...\n")

    # Read raw data from S3
    buoy_dyf, seismic_dyf, benchmark_dyf = read_raw_data()

    # Transform buoy data
    transformed_buoy_dyf = transform_buoy_data(buoy_dyf)

    # Write transformed data to S3 processed bucket
    write_to_s3(
        transformed_buoy_dyf,
        PROCESSED_BUCKET,
        "glue/buoy_transformed/",
        format="csv"
    )

    # Write to Glue Data Catalog
    write_to_glue_catalog(
        transformed_buoy_dyf,
        "surf_pipeline_db",
        "buoy_data_transformed"
    )

    # Commit Glue job
    job.commit()
    print("\n✓ Glue ETL job complete!")