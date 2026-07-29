from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from datetime import datetime, timedelta

# Default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5)
}

# Define DAG
dag = DAG(
    "surf_pipeline_aws",
    default_args=default_args,
    description="Cloud version of surf pipeline running on AWS MWAA",
    schedule_interval="0 6 * * 1",
    catchup=False,
    tags=["surf", "aws", "glue", "athena"]
)

with dag:
    # Sense if new raw data exists in S3
    sense_raw_data = S3KeySensor(
        task_id="sense_raw_data",
        bucket_name="surf-pipeline-raw-agl",
        bucket_key="raw/noaa_wave_data.json",
        aws_conn_id="aws_default",
        timeout=3600,
        poke_interval=300
    )

    # Run Glue ETL job
    run_glue_etl = GlueJobOperator(
        task_id="run_glue_etl",
        job_name="surf-pipeline-glue-etl",
        aws_conn_id="aws_default",
        region_name="us-east-1"
    )

    # Run Athena rankings query
    run_athena_rankings = AthenaOperator(
        task_id="run_athena_rankings",
        query="""
            SELECT
                location,
                MAX(wave_height_m) AS max_wave_height_m,
                ROUND(MAX(pct_of_nazare), 2) AS pct_of_nazare
            FROM surf_pipeline_db.buoy_data_transformed
            WHERE wave_height_m IS NOT NULL
            GROUP BY location
            ORDER BY max_wave_height_m DESC
        """,
        database="surf_pipeline_db",
        output_location="s3://surf-pipeline-final-agl/athena-results/",
        aws_conn_id="aws_default"
    )

    # Set dependencies
    sense_raw_data >> run_glue_etl >> run_athena_rankings