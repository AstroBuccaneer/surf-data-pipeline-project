# VPC Design

## Overview
The surf pipeline uses a VPC to isolate and secure AWS resources
from the public internet where necessary.

## Architecture

### VPC
- CIDR Block: 10.0.0.0/16
- Region: us-east-1

### Subnets
| Subnet | Type | CIDR | Availability Zone |
|---|---|---|---|
| surf-pipeline-subnet-1 | Private | 10.0.1.0/24 | us-east-1a |
| surf-pipeline-subnet-2 | Private | 10.0.2.0/24 | us-east-1b |
| surf-pipeline-subnet-public | Public | 10.0.3.0/24 | us-east-1a |

### Security Groups
| Resource | Inbound | Outbound |
|---|---|---|
| RDS | Port 5432 from Lambda SG only | None |
| Lambda | None | HTTPS 443 to internet |
| Glue | None | S3 and Glue endpoints only |

## Design Decisions
- RDS placed in private subnet — never publicly accessible
- Lambda functions in private subnet with NAT gateway for internet access
- S3 accessed via VPC endpoint — traffic never leaves AWS network
- Multi-AZ subnets for high availability
- Security groups follow least privilege — only required ports open

## VPC Endpoints
- S3 Gateway Endpoint — free, keeps S3 traffic inside AWS network
- Glue Interface Endpoint — keeps Glue traffic inside AWS network

## Why This Matters
Without a VPC your RDS database would be exposed to the public internet
which is a major security risk. The VPC acts as a private network inside
AWS that only your pipeline services can access.