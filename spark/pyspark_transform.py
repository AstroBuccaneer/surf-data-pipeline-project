from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os

# Paths
PROCESSED_PATH = "data/processed/"
FINAL_PATH = "data/final/"

# Create Spark session
spark = SparkSession.builder \
    .appName("SurfDataPipeline") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# Suppress verbose Spark logs
spark.sparkContext.setLogLevel("ERROR")

print("✓ Spark session started")

def load_data():
    """Load cleaned CSV files into Spark DataFrames."""

    print("Loading cleaned data into Spark...")

    buoy_df = spark.read.csv(
        f"{PROCESSED_PATH}buoy_data_clean.csv",
        header=True,
        inferSchema=True
    )

    storm_df = spark.read.csv(
        f"{PROCESSED_PATH}storm_data_clean.csv",
        header=True,
        inferSchema=True
    )

    seismic_df = spark.read.csv(
        f"{PROCESSED_PATH}seismic_data_clean.csv",
        header=True,
        inferSchema=True
    )

    print(f"✓ Buoy records loaded    : {buoy_df.count()}")
    print(f"✓ Storm records loaded   : {storm_df.count()}")
    print(f"✓ Seismic records loaded : {seismic_df.count()}")

    return buoy_df, storm_df, seismic_df

def transform_buoy_data(buoy_df):
    """Run PySpark transformations on buoy data."""

    print("\nTransforming buoy data with PySpark...")

    # Filter out null wave heights
    buoy_df = buoy_df.filter(F.col("wave_height_m").isNotNull())

    # Add wave height in feet column
    buoy_df = buoy_df.withColumn(
        "wave_height_ft",
        F.round(F.col("wave_height_m") * 3.28084, 2)
    )

    # Add benchmark percentage columns
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

    # Window function — rank wave heights per location
    window = Window.partitionBy("location").orderBy(
        F.col("wave_height_m").desc()
    )

    buoy_df = buoy_df.withColumn(
        "rank_within_location",
        F.rank().over(window)
    )

    print("✓ Buoy transformations complete")
    buoy_df.show(5)
    return buoy_df

def aggregate_by_location(buoy_df):
    """Aggregate buoy data by location using PySpark."""

    print("\nAggregating by location...")

    location_summary = buoy_df.groupBy("location").agg(
        F.count("wave_height_m").alias("total_readings"),
        F.round(F.max("wave_height_m"), 2).alias("max_wave_height_m"),
        F.round(F.avg("wave_height_m"), 2).alias("avg_wave_height_m"),
        F.round(F.max("wave_height_ft"), 2).alias("max_wave_height_ft"),
        F.round(F.max("pct_of_nazare"), 2).alias("max_pct_of_nazare"),
        F.sum(
            F.when(F.col("is_surfable") == "Yes", 1).otherwise(0)
        ).alias("surfable_readings")
    )

    # Add surfable percentage
    location_summary = location_summary.withColumn(
        "surfable_pct",
        F.round(
            F.col("surfable_readings") * 100.0 / F.col("total_readings"), 2
        )
    )

    # Rank locations by max wave height
    window = Window.orderBy(F.col("max_wave_height_m").desc())
    location_summary = location_summary.withColumn(
        "rank",
        F.rank().over(window)
    )

    location_summary = location_summary.orderBy("rank")

    print("✓ Location aggregation complete")
    location_summary.show()
    return location_summary

def save_results(buoy_df, location_summary):
    """Save PySpark results to final folder."""

    print("\nSaving PySpark results...")

    # Save transformed buoy data
    buoy_df.toPandas().to_csv(
        f"{FINAL_PATH}spark_buoy_transformed.csv",
        index=False
    )

    # Save location summary
    location_summary.toPandas().to_csv(
        f"{FINAL_PATH}spark_location_summary.csv",
        index=False
    )

    print(f"✓ Transformed buoy data saved to {FINAL_PATH}spark_buoy_transformed.csv")
    print(f"✓ Location summary saved to {FINAL_PATH}spark_location_summary.csv")


if __name__ == "__main__":
    print("Starting PySpark transformation pipeline...\n")

    # Load data
    buoy_df, storm_df, seismic_df = load_data()

    # Transform buoy data
    buoy_df = transform_buoy_data(buoy_df)

    # Aggregate by location
    location_summary = aggregate_by_location(buoy_df)

    # Save results
    save_results(buoy_df, location_summary)

    # Stop Spark session
    spark.stop()
    print("\n✓ PySpark pipeline complete!")

    