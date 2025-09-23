import os
from typing import Generator

import boto3
import pytest
from moto import mock_aws
from types_boto3_s3.client import S3Client

MOCK_AWS_BUCKET_NAME = "test-bucket"
MOCK_AWS_TEST_FILES = {
    "sample_pii_data": {
        "path": "tests/data/sample_pii_data.csv",
        "key": "sample_pii_data.csv",
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
    s3_client: S3Client, aws_credentials
) -> Generator[S3Client, None, None]:
    bucket_name = MOCK_AWS_BUCKET_NAME
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )
    yield s3_client


@pytest.fixture(scope="function")
def s3_client_with_files(
    s3_client_with_empty_test_bucket,
) -> Generator[S3Client, None, None]:
    s3_client = s3_client_with_empty_test_bucket

    with open(
        MOCK_AWS_TEST_FILES["sample_pii_data"]["path"],
        mode="rb",
    ) as sample_pii_data:
        s3_client.put_object(
            Bucket=MOCK_AWS_BUCKET_NAME,
            Key=MOCK_AWS_TEST_FILES["sample_pii_data"]["key"],
            Body=sample_pii_data,
        )

    yield s3_client
