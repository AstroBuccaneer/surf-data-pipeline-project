# 🌊 Surf Data Pipeline

## Project Overview
A production-grade end-to-end data pipeline comparing surf potential
across 4 US locations — Pensacola Beach, Cocoa Beach, Waikiki, and
Huntington Beach — scored against two world record benchmarks:

- **Lituya Bay, Alaska (1958)** — largest wave ever recorded (1,720 ft)
  caused by a magnitude 7.8 earthquake triggered rockslide
- **Nazaré, Portugal (2020)** — largest wave ever surfed (86 ft)
  by Sebastian Steudtner via underwater canyon amplification

## The So What
A data-driven answer to where and when to chase the best waves —
backed by 14 years of NOAA buoy data, USGS seismic records, and
NOAA storm events. Built as a production pipeline covering data
engineering, AWS, and machine learning — doubling as prep for
AWS SAA, DEA, and MLA certifications.

## Final Rankings
| Rank | Location | Surf Score | Key Strength |
|---|---|---|---|
| 1 | Waikiki | 67.41 | Consistent Pacific swells |
| 2 | Huntington Beach | 64.81 | Highest seismic activity |
| 3 | Cocoa Beach | 57.13 | Highest single wave recorded |
| 4 | Pensacola Beach | 53.47 | Most beginner friendly |

## Tech Stack
- **Languages:** Python, SQL
- **Data Engineering:** Pandas, PySpark, SQLite, Apache Airflow
- **AWS:** S3, Glue, Athena, Lambda, Kinesis, MWAA, Step Functions,
  SageMaker, Bedrock, Lake Formation, CloudWatch, CloudFormation
- **ML:** Scikit-learn, Random Forest, RAG, HuggingFace, FAISS
- **Infrastructure:** CloudFormation, VPC, IAM

## Data Sources
- NOAA NDBC — 14 years of hourly buoy readings (1.2M records)
- NOAA Storm Events — 23 years of hurricane and storm records
- USGS Earthquake API — seismic events within 500km per location
- Hardcoded benchmarks — Lituya Bay and Nazaré world records

## Project Architecture
See `docs/aws_architecture.md` for full architecture documentation
and `infrastructure/architecture.png` for visual diagram.

## Data Model
Star schema with 1 fact table and 4 dimension tables.
See `docs/data_model.md` for full documentation.

## Surf Score Formula
Three component weighted index scored against Nazaré benchmark.
See `docs/surf_score_formula.md` for full methodology.

## ML Model
Random Forest predicting next month wave height.
- Training samples: 513
- Test samples: 129
- R2: 0.7044
- RMSE: 0.2446 meters

## RAG System
Natural language Q&A against surf research knowledge base.
- 4 knowledge base documents
- 12 FAISS embeddings
- HuggingFace all-MiniLM-L6-v2 embeddings

## Project Build Log

### Day 1 
- Created full project folder structure across all 4 phases
- Initialized GitHub repository and pushed initial structure

### Day 2
- Created `config.yaml` as the central source of truth for the entire pipeline
- Configured all 4 surf locations (Pensacola Beach, Cocoa Beach, Waikiki, 
  Huntington Beach) with coordinates and NOAA buoy IDs
- Added both world record benchmarks (Lituya Bay 1720ft, Nazaré 86ft) 
  with cause metadata and surfability flags
- Set up scoring weights for surf potential index
- Configured data paths and AWS placeholders for future phases
- Created `.env` file locally to store API keys securely (not pushed to GitHub)
- Created `.gitignore` to protect sensitive files, API keys, and data folders
  from being pushed to GitHub
- Registered for NOAA API token for Day 3 data extraction

### Day 3
- Built `extract/noaa_buoy.py` to pull live NOAA NDBC buoy data
- Successfully pulling real wave height, swell, and wind data for all 4 locations
- Raw data saved to `data/raw/noaa_wave_data.json`

**Debugging Notes:**
- Initially used NOAA CDO API with `LOCAL_CLIMATOLOGICAL_DATA` → got 500 error
  (wrong API for ocean buoy data)
- Switched to NOAA CO-OPS API with `waves` product → got 400 error
  (CO-OPS doesn't support wave height as a product)
- Switched to NOAA NDBC (National Data Buoy Center) → success
  (NDBC is the correct source for ocean buoy wave height, swell period, and wind speed)

  ### Day 4
- Built `extract/noaa_storms.py` to pull NOAA Storm Events data for all 4 locations
- Debugged Storm Events API — switched to direct CSV file downloads
- Built directory listing scraper to find exact filenames dynamically
- Added idempotency checkpoint system — saves each year individually so 
  pipeline resumes where it left off if connection drops
- Lost connection mid-run on Huntington Beach 2005, restarted and checkpoint 
  system skipped already completed Florida files automatically
- Successfully pulled storm data 2000-2023 for Florida, Hawaii, and California

**Debugging Notes:**
- ChunkedEncodingError caused by unstable network dropping mid-download
- Fixed with idempotency checkpoint pattern — production standard for 
  long running network dependent pipelines

  ### Day 5
- Built `extract/usgs_seismic.py` to pull USGS earthquake data for all 4 locations
- Used lat/lon coordinates from config.yaml to search within 500km radius
- Filtered to magnitude 4.0+ events ordered by magnitude
- Results already showing story: Huntington Beach (830) and Waikiki (253) 
  have far more seismic activity than Pensacola (6) and Cocoa Beach (1)
- Seismic frequency feeds directly into surf score causative factor weighting

**Design Decisions:**
- `radius_km=500` — wide enough to catch offshore seismic events that 
  could generate waves toward each location
- `minmagnitude=4.0` — filters out small earthquakes that wouldn't affect 
  wave conditions
- `orderby=magnitude` — returns the biggest events first which is perfect 
  for benchmark comparison against Lituya Bay's 7.8 magnitude trigger

  ### Day 6
- Built `extract/benchmarks.py` with hardcoded world record reference data
- Lituya Bay 1958 — 1720ft megatsunami, seismic cause, not surfable (upper bound)
- Nazaré 2020 — 86ft by Sebastian Steudtner, swell amplification cause, surfable (scoring ceiling)
- Benchmarks saved to `data/raw/benchmarks.json`

**Design Decision:**
- Lituya Bay hardcoded permanently — geological event that will never change
- Nazaré treated as dynamic in future — WSL records could be broken and 
  would need automatic updating via Airflow DAG in Phase 3


  ### Day 7
- Built `transform/clean.py` to normalize all raw data sources
- Parsed NOAA NDBC text format into structured records
- Handled missing values marked as `MM` converting to null
- Standardized column names across all 4 locations
- Results: 21,462 buoy records, 130,012 storm records, 
  1,090 seismic records, 2 benchmarks
- All cleaned data saved to `data/processed/`

**Design Decisions:**
- Parsed raw NOAA NDBC text format into structured records
- Handled missing values marked as `MM` by converting to None/null
- Standardized column names across all 4 locations
- Wave height kept in meters for consistency
- Saved as CSV for easy loading into star schema

### Day 8
- Built `transform/schema.py` to create star schema in SQLite
- dim_location: 4 surf locations with coordinates and buoy IDs
- dim_cause: 5 cause types (hurricane, tropical storm, pacific swell, seismic, swell amplification)
- dim_date: 8,766 days from 2000-2023 tagged with season and hurricane season flag
- dim_benchmark: 2 world records (Lituya Bay and Nazaré)
- wave_events: 21,462 fact records with benchmark percentage scores vs Nazaré and Lituya Bay
- Star schema saved to data/final/surf_pipeline.db

**Design Decisions:**
- Every buoy reading scored as percentage of both benchmarks directly in fact table
- Date dimension includes hurricane season flag for seasonal surf analysis
- Star schema chosen over snowflake for simplicity and query performance

### Day 9
- Built `transform/score.py` to calculate surf potential index
- Three scoring components:
  - Peak magnitude score (50% weight) — max wave height vs Nazaré benchmark
  - Surfable frequency score (30% weight) — % of readings above 1.5m
  - Seismic recurrence score (20% weight) — earthquake frequency and severity
- Final Rankings:
  1. Huntington Beach — 81.91
  2. Waikiki — 55.44
  3. Pensacola Beach — 46.51
  4. Cocoa Beach — 41.05
- Scores saved to data/processed/surf_scores.csv

**Key Insights:**
- Huntington Beach wins due to 830 seismic events and 39.71% surfable frequency
- Waikiki strong due to consistent Pacific swells and 253 seismic events
- Pensacola hurt by low frequency despite recording second highest single wave
- Cocoa Beach most sheltered — only 1 seismic event and 2% surfable frequency


### Day 10
- Built `sql/create_tables.sql` — star schema DDL definitions
- Built `sql/rankings.sql` — location rankings using joins, window functions, CTEs
- Built `sql/analysis.sql` — deep analysis including year over year trends, 
  best month to surf, Nazaré gap analysis, and quarterly rankings
- SQL files ready to run against SQLite locally and Athena in Phase 3

**SQL Concepts Covered:**
- Joins (fact to dimension tables)
- CTEs (hurricane season comparison)
- Window functions (RANK, ROW_NUMBER, rolling averages)
- Aggregations (GROUP BY, HAVING)
- Conditional aggregations (CASE WHEN)


### Day 11
- Built `spark/pyspark_transform.py` to reprocess data at scale with PySpark
- Fixed Java version error — upgraded from Java 8 to Java 17
- Successfully loaded 21,462 buoy, 130,012 storm, 1,090 seismic records into Spark
- PySpark transformations mirror pandas version confirming data consistency
- Results saved to data/final/

**PySpark vs Pandas:**
- F.when() is equivalent to CASE WHEN in SQL
- Window.partitionBy() is equivalent to PARTITION BY in SQL
- F.rank().over(window) is your window function in Python
- spark.sql.shuffle.partitions set to 4 for small local dataset

**Debugging Notes:**
- Java UnsupportedClassVersionError — PySpark requires Java 17+
- Fixed by downloading Java 17 and setting JAVA_HOME environment variable
- PyArrow warning is non-critical — Spark fell back to non-optimized conversion


### Day 12
- Built `dags/surf_pipeline_dag.py` — Airflow DAG orchestrating full pipeline
- 7 tasks defined across extract and transform phases
- All 4 extract tasks run in parallel, then clean, schema, score run in sequence
- Scheduled to run every Monday at 6am via cron expression
- DAG ready to deploy to AWS MWAA in Phase 3

**DAG Design Decisions:**
- retries: 2 — automatically retries failed tasks twice before giving up
- retry_delay: 5 minutes — waits between retries
- schedule_interval: 0 6 * * 1 — cron for every Monday at 6am
- catchup=False — don't backfill missed runs if pipeline was down
- Parallel extract tasks reduce total pipeline runtime significantly

**What is a DAG:**
Directed Acyclic Graph — Airflow's blueprint for pipeline orchestration.
Defines tasks, dependencies, and schedule so pipeline runs automatically
without manual intervention.


### Day 13
- Configured AWS CLI with IAM user credentials
- Created 3 S3 buckets following least privilege IAM best practices
  - surf-pipeline-raw-agl
  - surf-pipeline-processed-agl
  - surf-pipeline-final-agl
- Built `load/s3_loader.py` to upload all pipeline data to S3
- Successfully uploaded 11 files to S3 data lake
- Raw, processed, and final data now living in the cloud

**AWS Best Practices Applied:**
- Never used root account access keys
- Created IAM user with only required permissions
- Principle of least privilege — IAM user only has permissions needed
- S3 bucket names include initials for global uniqueness


### Day 14
- Completed AWS Foundations layer covering SAA exam domains
- Built all CloudFormation infrastructure as code files
- Configured CloudWatch monitoring and alerting
- Designed VPC architecture for secure resource isolation

**Files Built:**
- `cloudformation/s3_buckets.yaml` — S3 bucket definitions with versioning
- `cloudformation/iam.yaml` — IAM roles for Lambda, Glue, and Step Functions
- `cloudformation/lambda.yaml` — Lambda function definitions for pipeline tasks
- `cloudformation/rds.yaml` — RDS PostgreSQL database definition
- `cloudwatch_alerts.json` — 3 alarms for pipeline failures, duration, and S3 errors
- `iam_roles.md` — IAM roles and permissions documentation
- `vpc_design.md` — VPC architecture with private subnets and security groups
- `s3_lifecycle_policy.json` — Cost optimization via S3 storage tier transitions

**AWS Concepts Covered (SAA Exam):**
- Infrastructure as Code with CloudFormation
- IAM roles and principle of least privilege
- VPC design with public and private subnets
- Security groups and network isolation
- S3 storage classes and lifecycle policies for cost optimization
- CloudWatch alarms for pipeline monitoring
- RDS in private subnet for security
- S3 VPC endpoints keeping traffic inside AWS network

**Key Design Decisions:**
- RDS placed in private subnet — never publicly accessible
- S3 lifecycle policy moves raw data to Glacier after 180 days saving costs
- CloudWatch alarms trigger on Lambda errors and duration exceeding 4 minutes
- All infrastructure defined as code — can be redeployed anywhere in minutes


### Day 15
- Built full AWS Data Engineering layer covering DEA exam domains
- Completed all files in `aws_data_engineering/` folder

**Files Built:**
- `glue/glue_etl_job.py` — Glue ETL job replacing local transform scripts
- `glue/glue_crawler_config.json` — Crawler to catalog all S3 buckets
- `athena/rankings.sql` — Athena ranking queries against S3 data
- `athena/analysis.sql` — Athena deep analysis with partitioning
- `lake_formation/access_policy.md` — Fine grained data lake access control
- `kinesis/producer.py` — Live buoy stream polling NOAA every hour
- `kinesis/consumer.py` — Reads from Kinesis and saves to database
- `kinesis/stream_config.json` — Kinesis stream configuration
- `mwaa/surf_pipeline_dag.py` — Cloud Airflow DAG using Glue and Athena operators
- `step_functions/pipeline_state_machine.json` — Step Functions orchestration

**AWS Concepts Covered (DEA Exam):**
- Glue ETL jobs and DynamicFrames
- Glue Data Catalog and crawlers
- Athena SQL queries against S3 with partition pruning
- Lake Formation fine grained access control
- Kinesis Data Streams — producer and consumer pattern
- PartitionKey routing data to correct Kinesis shard
- MWAA managed Airflow with AWS operators
- Step Functions parallel state execution
- S3KeySensor waiting for data before pipeline runs
- Retry logic with exponential backoff

**Kinesis Design:**
- Producer polls NOAA NDBC every hour and sends to Kinesis stream
- PartitionKey ensures same location always goes to same shard
- Consumer reads from stream, calculates benchmark percentages,
  flags surfable readings and saves to wave_events fact table
- RetentionPeriodHours: 24 keeps data available for 24 hours

### Day 16
- Built `ml/sagemaker/preprocessing.py` for ML feature engineering
- Discovered NOAA NDBC realtime API only returns 45 days of data
- Fixed by switching to NOAA NDBC historical endpoint
- Extended date range from 2020 to 2010 for better ML training data
- Fixed 99.0 missing data code being read as real wave height
- Final dataset: 603,807 buoy records, 646 monthly features
- Train/test split: 513 training, 129 test records, 15 features

**Key Lessons:**
- Data range directly impacts ML model accuracy
- Always validate data ranges before training
- 99.0 is a common NOAA missing data sentinel value
- More historical data revealed Waikiki as top ranked location
  changing results from the 4 year dataset

**Files Updated:**
- `extract/noaa_buoy.py` — switched to historical endpoint, extended to 2010
- `transform/clean.py` — added < 30m filter to catch 99.0 sentinel values


### Day 17
- Built `ml/sagemaker/train.py` training 3 ML models
- Models compared: Linear Regression, Random Forest, Gradient Boosting
- Winner: Random Forest — RMSE 0.2446, MAE 0.1850, R2 0.7044
- Fixed NaN values using SimpleImputer with mean strategy
- Top features: avg wave height (27.8%), Nazaré % (17%), surfable % (15%)
- Best model saved to data/final/best_model.pkl

**Model Evaluation Metrics:**
- RMSE — average prediction error in meters
- MAE — mean absolute error in meters  
- R2 — how well model explains variance (0.70 is solid for weather data)

**Key Insight:**
Historical wave patterns and seasonality are the strongest predictors
of future surf conditions — confirmed by feature importance analysis

**Debugging Notes:**
- ValueError: Input X contains NaN — fixed with SimpleImputer mean strategy

**Why Random Forest Won:**
- Handles non-linear relationships between wave height and season
- Less sensitive to outliers than Linear Regression
- More interpretable than Gradient Boosting via feature importance
- 70% R2 is strong for oceanographic prediction — weather data is 
  inherently noisy so perfect prediction is impossible


  ### Day 18
- Built `ml/sagemaker/evaluate.py` — deep model evaluation
- Built `ml/sagemaker/deploy.py` — deployment simulation with S3 upload
- Model uploaded to s3://surf-pipeline-final-agl/models/

**Evaluation Results:**
- RMSE: 0.2446m — predictions off by 24cm on average
- MAE: 0.1849m — mean absolute error
- R2: 0.7044 — explains 70% of wave variance
- MAPE: 15% — average percentage error
- 72.1% of predictions within 20% of actual value
- 97.7% of predictions within 50% of actual value

**Deployment:**
- Model serialized with pickle and uploaded to S3
- Endpoint simulation predicts next month wave height per location
- Predictions uploaded to S3 for downstream consumption
- In production this would be a live SageMaker endpoint serving
  real time predictions via REST API

**MLOps Patterns Applied:**
- Model versioning via metadata JSON
- Artifacts stored in S3 with clear naming convention
- Evaluation separate from training for clean auditing
- Predictions uploaded to S3 for downstream consumption

### Day 19
- Built full RAG pipeline in `ml/rag/`
- `embeddings.py` — chunks and embeds knowledge base into FAISS vector store
- `retriever.py` — semantic search retrieving relevant context per query
- `generator.py` — synthesizes answers from retrieved context
- Knowledge base covers benchmarks, locations, surf scores, beginner guide
- Added beginner surf location document expanding knowledge base to 4 docs
- 12 embeddings in FAISS vector store

**RAG Pipeline Flow:**
1. Documents chunked into 500 character pieces with 50 char overlap
2. HuggingFace all-MiniLM-L6-v2 converts chunks to vector embeddings
3. FAISS stores embeddings for fast similarity search
4. Query converted to embedding and compared against stored vectors
5. Top 3 most similar chunks retrieved as context
6. Context passed to generator to synthesize answer

**Why HuggingFace over OpenAI:**
- Completely free — no API costs
- Runs locally — no data leaves machine
- Open source — no vendor lock in
- Production viable — many companies use open source embeddings

**In Production:**
- Would use AWS Bedrock instead of simple text generator
- Bedrock would generate natural language answers from retrieved context
- Knowledge base would auto update when new NOAA reports published



## Test Suite
45 unit tests across 3 test files — all passing

- `tests/test_extract.py` — 11 tests covering benchmarks and raw data files
- `tests/test_transform.py` — 15 tests covering cleaned data and star schema
- `tests/test_score.py` — 19 tests covering surf scores, SQL queries, and ML outputs

Run tests:
\```bash
pytest tests/ -v
\```


### Day 20
- Completed `notebooks/exploration.ipynb` with 6 EDA charts
- Built 3 master runner scripts in `scripts/` folder
- Completed all docs — data model, surf score formula, 
  benchmark research, AWS architecture
- All 45 unit tests passing
- Project fully complete and pushed to GitHub

**Charts Built:**
- Surf potential rankings
- Average wave height by location
- Seismic events by location
- Monthly wave height patterns
- Benchmark comparison vs Nazaré
- Final EDA summary


## Installation

```bash
git clone https://github.com/AstroBuccaneer/surf-data-pipeline
cd surf-data-pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```