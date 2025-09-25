"""IAM roles and policies for GDPR obfuscation"""

import pulumi_aws as aws
from pulumi import Output


def create_lambda_role(account_id: str, aws_region: str, lambda_name: str):
    """
    Create a Lambda role with the necessary policies for GDPR obfuscation

    :param account_id: AWS account ID
    :param aws_region: AWS region
    :param lambda_name: Name of the Lambda function
    :return: Lambda role, Lambda S3 policy, and Lambda S3 policy attachment

    """
    # ------------------------------
    # Lambda IAM Role Creation
    # ------------------------------
    lambda_assume_role_policy_doc = aws.iam.get_policy_document(
        version="2012-10-17",
        statements=[
            {
                "effect": "Allow",
                "principals": [
                    {
                        "type": "Service",
                        "identifiers": ["lambda.amazonaws.com"],
                    }
                ],
                "actions": ["sts:AssumeRole"],
            }
        ],
    )

    lambda_role = aws.iam.Role(
        f"{lambda_name}-lambda-role",
        assume_role_policy=lambda_assume_role_policy_doc.json,
        tags={
            "Project": "GDPR Obfuscator",
            "Environment": "Dev",
        },
    )

    # ------------------------------
    # Lambda IAM Policies for Lambda Logging on CloudWatch
    # ------------------------------

    # Define
    lambda_logging_policy_doc = aws.iam.get_policy_document(
        version="2012-10-17",
        statements=[
            {
                "effect": "Allow",
                "actions": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                "resources": [
                    f"arn:aws:logs:{aws_region}:{account_id}:log-group:/aws/lambda/{lambda_name}:*"
                ],
            }
        ],
    )
    # Create
    lambda_logging_policy = aws.iam.Policy(
        f"{lambda_name}-lambda-logging-policy",
        policy=lambda_logging_policy_doc.json,
    )

    # Attach
    lambda_logging_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{lambda_name}-lambda-logging-policy-attachment",
        role=lambda_role.name,
        policy_arn=lambda_logging_policy.arn,
    )

    return {
        "lambda_role": lambda_role,
        "lambda_logging_policy_attachment": lambda_logging_policy_attachment,
    }


def create_lambda_s3_policies(
    lambda_role_name: str, bucket_name: str, bucket_arn: str, lambda_name: str
):
    """
    Create S3 access policies for Lambda

    :param lambda_role: Lambda role
    :param bucket_name: S3 bucket name (Output)
    :param bucket_arn: S3 bucket ARN
    :param lambda_name: Name of the Lambda function
    :return: Lambda S3 policy and Lambda S3 policy attachment
    """

    # Define
    lambda_s3_policy_doc = aws.iam.get_policy_document(
        statements=[
            {
                "effect": "Allow",
                "actions": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:DeleteObject",
                ],
                "resources": [bucket_arn],
            }
        ],
    )

    # Create policy with static name
    lambda_s3_policy = aws.iam.Policy(
        f"{lambda_name}-{bucket_name}-lambda-s3-policy",
        policy=lambda_s3_policy_doc.json,
    )

    # Attach
    lambda_s3_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{lambda_name}-{bucket_name}-lambda-s3-policy-attachment",
        role=lambda_role_name,
        policy_arn=lambda_s3_policy.arn,
    )

    return {
        "lambda_s3_policy": lambda_s3_policy,
        "lambda_s3_policy_attachment": lambda_s3_policy_attachment,
    }
