import json
import os
import boto3
from datetime import datetime

# AWS config
REGION = "us-east-1"
S3_BUCKET = "surf-pipeline-final-agl"
ROLE_ARN = "arn:aws:iam::YOUR_ACCOUNT_ID:role/surf-pipeline-role"

print("✓ SageMaker Pipeline initialized")


def define_pipeline():
    """Define SageMaker Pipeline for automated retraining."""

    pipeline_definition = {
        "Version": "2020-12-01",
        "Metadata": {},
        "Parameters": [
            {
                "Name": "InputDataUrl",
                "Type": "String",
                "DefaultValue": f"s3://{S3_BUCKET}/processed/buoy_data_clean.csv"
            },
            {
                "Name": "ModelOutputUrl",
                "Type": "String",
                "DefaultValue": f"s3://{S3_BUCKET}/models/"
            },
            {
                "Name": "TrainingInstanceType",
                "Type": "String",
                "DefaultValue": "ml.m5.large"
            }
        ],
        "Steps": [
            {
                "Name": "PreprocessingStep",
                "Type": "Processing",
                "Arguments": {
                    "ProcessingInputs": [
                        {
                            "InputName": "input-data",
                            "S3Input": {
                                "S3Uri": f"s3://{S3_BUCKET}/processed/",
                                "LocalPath": "/opt/ml/processing/input",
                                "S3DataType": "S3Prefix"
                            }
                        }
                    ],
                    "ProcessingOutputs": [
                        {
                            "OutputName": "train-data",
                            "S3Output": {
                                "S3Uri": f"s3://{S3_BUCKET}/pipeline/train/",
                                "LocalPath": "/opt/ml/processing/output/train"
                            }
                        },
                        {
                            "OutputName": "test-data",
                            "S3Output": {
                                "S3Uri": f"s3://{S3_BUCKET}/pipeline/test/",
                                "LocalPath": "/opt/ml/processing/output/test"
                            }
                        }
                    ],
                    "AppSpecification": {
                        "ImageUri": "YOUR_ECR_IMAGE_URI",
                        "ContainerEntrypoint": [
                            "python3",
                            "/opt/ml/processing/ml/sagemaker/preprocessing.py"
                        ]
                    }
                }
            },
            {
                "Name": "TrainingStep",
                "Type": "Training",
                "Arguments": {
                    "AlgorithmSpecification": {
                        "TrainingInputMode": "File",
                        "TrainingImage": "YOUR_ECR_IMAGE_URI"
                    },
                    "InputDataConfig": [
                        {
                            "ChannelName": "train",
                            "DataSource": {
                                "S3DataSource": {
                                    "S3Uri": f"s3://{S3_BUCKET}/pipeline/train/",
                                    "S3DataType": "S3Prefix"
                                }
                            }
                        }
                    ],
                    "OutputDataConfig": {
                        "S3OutputPath": f"s3://{S3_BUCKET}/pipeline/model/"
                    },
                    "ResourceConfig": {
                        "InstanceType": "ml.m5.large",
                        "InstanceCount": 1,
                        "VolumeSizeInGB": 30
                    },
                    "StoppingCondition": {
                        "MaxRuntimeInSeconds": 3600
                    }
                }
            },
            {
                "Name": "EvaluationStep",
                "Type": "Processing",
                "Arguments": {
                    "ProcessingInputs": [
                        {
                            "InputName": "model",
                            "S3Input": {
                                "S3Uri": f"s3://{S3_BUCKET}/pipeline/model/",
                                "LocalPath": "/opt/ml/processing/model"
                            }
                        },
                        {
                            "InputName": "test-data",
                            "S3Input": {
                                "S3Uri": f"s3://{S3_BUCKET}/pipeline/test/",
                                "LocalPath": "/opt/ml/processing/test"
                            }
                        }
                    ],
                    "ProcessingOutputs": [
                        {
                            "OutputName": "evaluation",
                            "S3Output": {
                                "S3Uri": f"s3://{S3_BUCKET}/pipeline/evaluation/",
                                "LocalPath": "/opt/ml/processing/evaluation"
                            }
                        }
                    ],
                    "AppSpecification": {
                        "ImageUri": "YOUR_ECR_IMAGE_URI",
                        "ContainerEntrypoint": [
                            "python3",
                            "/opt/ml/processing/ml/sagemaker/evaluate.py"
                        ]
                    }
                }
            },
            {
                "Name": "RegisterModelStep",
                "Type": "RegisterModel",
                "Arguments": {
                    "ModelPackageGroupName": "surf-pipeline-model-group",
                    "ModelMetrics": {
                        "ModelQuality": {
                            "Statistics": {
                                "ContentType": "application/json",
                                "S3Uri": f"s3://{S3_BUCKET}/pipeline/evaluation/"
                            }
                        }
                    },
                    "InferenceSpecification": {
                        "Containers": [
                            {
                                "Image": "YOUR_ECR_IMAGE_URI",
                                "ModelDataUrl": f"s3://{S3_BUCKET}/pipeline/model/"
                            }
                        ],
                        "SupportedContentTypes": ["application/json"],
                        "SupportedResponseMIMETypes": ["application/json"]
                    },
                    "ModelApprovalStatus": "PendingManualApproval"
                }
            }
        ]
    }

    return pipeline_definition


def save_pipeline_definition(pipeline_definition):
    """Save pipeline definition to file."""

    output_path = "data/final/sagemaker_pipeline.json"
    with open(output_path, "w") as f:
        json.dump(pipeline_definition, f, indent=4)

    print(f"✓ Pipeline definition saved to {output_path}")


if __name__ == "__main__":
    print("Defining SageMaker Pipeline...\n")

    pipeline_definition = define_pipeline()
    save_pipeline_definition(pipeline_definition)

    print("\n--- Pipeline Summary ---")
    print(f"Pipeline steps  : {len(pipeline_definition['Steps'])}")
    for step in pipeline_definition["Steps"]:
        print(f"  - {step['Name']} ({step['Type']})")

    print(f"\nS3 bucket       : {S3_BUCKET}")
    print(f"Region          : {REGION}")
    print("\n✓ SageMaker Pipeline definition complete!")
    print("\nNote: Deploy to AWS SageMaker Pipelines console")
    print("      replacing YOUR_ECR_IMAGE_URI with actual ECR image")