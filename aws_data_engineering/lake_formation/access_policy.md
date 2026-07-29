# Lake Formation Access Policy

## Overview
AWS Lake Formation manages fine-grained access control to the surf pipeline
data lake. Instead of managing S3 bucket policies directly Lake Formation
lets you control access at the database, table, and column level.

## Data Lake Structure

### Databases
| Database | Description |
|---|---|
| surf_pipeline_db | Main surf pipeline database |

### Tables
| Table | S3 Location | Description |
|---|---|---|
| buoy_data_transformed | s3://surf-pipeline-processed-agl/glue/buoy_transformed/ | Cleaned buoy wave data |
| storm_data_clean | s3://surf-pipeline-processed-agl/processed/storm_data_clean.csv | Storm event records |
| seismic_data_clean | s3://surf-pipeline-processed-agl/processed/seismic_data_clean.csv | Seismic event records |
| benchmarks_clean | s3://surf-pipeline-processed-agl/processed/benchmarks_clean.csv | World record benchmarks |
| surf_scores | s3://surf-pipeline-processed-agl/processed/surf_scores.csv | Final surf potential scores |

## Access Control

### Permissions by Role
| Role | Database | Tables | Columns | Access Level |
|---|---|---|---|---|
| surf-pipeline-role | surf_pipeline_db | ALL | ALL | Full access |
| analyst-role | surf_pipeline_db | buoy_data_transformed, surf_scores | ALL | Select only |
| ml-role | surf_pipeline_db | ALL | ALL | Select only |

## Column Level Security
Sensitive columns can be restricted per role:
- Location coordinates (lat/lon) — restricted to surf-pipeline-role only
- Raw API responses — restricted to surf-pipeline-role only

## Why Lake Formation Over S3 Bucket Policies
- Centralized access control across all tables
- Column level security not possible with S3 policies alone
- Row level filtering for multi tenant scenarios
- Audit logging of all data access
- Works seamlessly with Glue, Athena, and SageMaker

## Interview Talking Point
Lake Formation lets you say yes to the question
"how do you control who sees what data in your data lake?"
without managing dozens of S3 bucket policies manually.