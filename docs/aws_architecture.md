# AWS Architecture Documentation

## Overview
The surf pipeline uses a multi-layer AWS architecture covering
data ingestion, transformation, querying, orchestration, and
machine learning across 3 AWS exam domains.

## Architecture Diagram
See `infrastructure/architecture.png` for visual diagram.

## Data Flow

NOAA NDBC API ──→ Lambda Extract ──→ S3 Raw
NOAA Storms ──→ Lambda Extract ──→ S3 Raw
USGS Seismic ──→ Lambda Extract ──→ S3 Raw
│
Glue ETL
│
S3 Processed
│
Athena SQL
│
S3 Final
│
SageMaker ML
│
Bedrock RAG


## Services by Phase

### Phase 2 — AWS Foundations (SAA)
| Service | Purpose | Config |
|---|---|---|
| S3 | Data lake storage | 3 buckets — raw, processed, final |
| IAM | Access control | surf-pipeline-role with least privilege |
| Lambda | Serverless compute | 4 functions — extract and transform |
| CloudWatch | Monitoring | 3 alarms — failure, duration, S3 errors |
| VPC | Network isolation | Private subnets for RDS and Lambda |
| RDS | Metadata storage | PostgreSQL db.t3.micro free tier |
| CloudFormation | Infrastructure as code | 4 stacks — S3, IAM, Lambda, RDS |

### Phase 3 — Data Engineering (DEA)
| Service | Purpose | Config |
|---|---|---|
| Glue ETL | Cloud transformation | Replaces local transform scripts |
| Glue Crawler | Schema discovery | Crawls all 3 S3 buckets |
| Glue Data Catalog | Metadata store | surf_pipeline_db database |
| Athena | SQL on S3 | Rankings and analysis queries |
| Lake Formation | Access control | Column level security |
| Kinesis | Live streaming | 1 shard hourly buoy polling |
| MWAA | Managed Airflow | Weekly pipeline orchestration |
| Step Functions | Alternative orchestration | Parallel extract state machine |

### Phase 4 — Machine Learning (MLA)
| Service | Purpose | Config |
|---|---|---|
| SageMaker Processing | Feature engineering | 603k records preprocessed |
| SageMaker Training | Model training | Random Forest R2 0.7044 |
| SageMaker Endpoint | Predictions | Next month wave height per location |
| SageMaker Pipelines | MLOps | Auto retrain on new data |
| SageMaker Feature Store | Feature management | 15 surf features stored |
| Bedrock | RAG generation | Natural language surf Q&A |
| OpenSearch Serverless | Vector store | Embedding storage for RAG |

## S3 Bucket Structure

surf-pipeline-raw-agl/
├── raw/
│ ├── noaa_wave_data.json
│ ├── noaa_storm_data.json
│ ├── usgs_seismic_data.json
│ └── benchmarks.json

surf-pipeline-processed-agl/
├── processed/
│ ├── buoy_data_clean.csv
│ ├── storm_data_clean.csv
│ ├── seismic_data_clean.csv
│ ├── benchmarks_clean.csv
│ └── surf_scores.csv
├── glue/
│ └── buoy_transformed/

surf-pipeline-final-agl/
├── final/
│ ├── spark_buoy_transformed.csv
│ └── spark_location_summary.csv
├── models/
│ ├── best_model.pkl
│ ├── model_metadata.json
│ ├── evaluation_report.json
│ └── surf_predictions.json
└── athena-results/

