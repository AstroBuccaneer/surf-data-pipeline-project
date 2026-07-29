# IAM Roles & Permissions Design

## Overview
The surf pipeline follows the principle of least privilege — every service
only has the minimum permissions needed to perform its job.

## Roles

### surf-pipeline-role
Used by Lambda, Glue, and Step Functions to access AWS services.

**Permissions:**
- AmazonS3FullAccess — read/write to all 3 S3 buckets
- AWSGlueFullAccess — run Glue ETL jobs and crawlers
- AmazonAthenaFullAccess — run SQL queries against S3 data
- CloudWatchFullAccess — write logs and metrics

**Trusted Services:**
- lambda.amazonaws.com
- glue.amazonaws.com
- states.amazonaws.com

## IAM Best Practices Applied
- Root account access keys never created or used
- IAM user created for CLI access with only required permissions
- Service roles used for all AWS service to service communication
- No hardcoded credentials in code — all loaded from environment variables
- Access keys stored in .env file which is excluded from GitHub via .gitignore

## Principle of Least Privilege
Each service only gets access to what it needs:
- Lambda extract functions — S3 raw bucket write only
- Lambda transform functions — S3 processed bucket read/write
- Glue jobs — S3 read/write and Glue catalog access
- Athena — S3 read and Athena query execution only