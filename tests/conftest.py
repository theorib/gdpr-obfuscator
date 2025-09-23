import os
from typing import Generator

import boto3
import pytest
from moto import mock_aws
from types_boto3_s3.client import S3Client


@pytest.fixture(scope="package")
def mock_aws_bucket_name():
    return "test-bucket"


@pytest.fixture(scope="package")
def test_files():
    return {
        "csv": {
            "sample_pii_data": {
                "path": "tests/data/sample_pii_data.csv",
                "key": "sample_pii_data.csv",
            }
        }
    }


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-west-2"


@pytest.fixture(scope="function")
def s3_client(aws_credentials) -> Generator[S3Client, None, None]:
    with mock_aws():
        client: S3Client = boto3.client("s3", region_name="eu-west-2")

        yield client


@pytest.fixture(scope="function")
def s3_client_with_empty_test_bucket(
    s3_client: S3Client, aws_credentials, mock_aws_bucket_name
) -> Generator[S3Client, None, None]:
    bucket_name = mock_aws_bucket_name
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )
    yield s3_client


@pytest.fixture(scope="function")
def s3_client_with_files(
    s3_client_with_empty_test_bucket, test_files, mock_aws_bucket_name
) -> Generator[S3Client, None, None]:
    s3_client = s3_client_with_empty_test_bucket

    with open(
        test_files["csv"]["sample_pii_data"]["path"],
        mode="rb",
    ) as sample_pii_data:
        s3_client.put_object(
            Bucket=mock_aws_bucket_name,
            Key=test_files["csv"]["sample_pii_data"]["key"],
            Body=sample_pii_data,
        )

    yield s3_client
