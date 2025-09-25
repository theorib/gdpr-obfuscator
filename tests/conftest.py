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
def masking_string():
    return "***"


@pytest.fixture(scope="package")
def test_files():
    return {
        "csv": {
            "simple_pii_data": {
                "local_path": "tests/data/simple_pii_data.csv",
                "result_local_path": "tests/data/simple_pii_data_obfuscated.csv",
                "key": "simple_pii_data.csv",
                "pii_fields": ["email_address"],
            },
            "edge_cases_no_rows": {
                "local_path": "tests/data/edge_cases_no_rows.csv",
                "result_local_path": "tests/data/edge_cases_no_rows.csv",
                "key": "edge_cases_no_rows.csv",
            },
            "complex_pii_data": {
                "local_path": "tests/data/complex_pii_data.csv",
                "result_local_path": "tests/data/complex_pii_data_obfuscated.csv",
                "key": "complex_pii_data.csv",
                "result_key": "complex_pii_data_obfuscated.csv",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
            "edge_cases_non_standard_chars": {
                "local_path": "tests/data/edge_cases_non_standard_chars.csv",
                "result_local_path": "tests/data/edge_cases_non_standard_chars_obfuscated.csv",
                "key": "edge_cases_non_standard_chars.csv",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                ],
            },
            "edge_cases_missing_data": {
                "local_path": "tests/data/edge_cases_missing_data.csv",
                "result_local_path": "tests/data/edge_cases_missing_data_obfuscated.csv",
                "key": "edge_cases_missing_data.csv",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
            "edge_cases_empty_file": {
                "local_path": "tests/data/edge_cases_empty_file.csv",
                "key": "edge_cases_empty_file.csv",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
        }
    }


@pytest.fixture(scope="class")
def get_test_file():
    def get_test_file_inner_factory(local_path: str):
        with open(local_path, mode="rb") as file:
            return file.read()

    yield get_test_file_inner_factory


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

    for file in test_files["csv"].values():
        with open(file["local_path"], mode="rb") as f:
            s3_client.put_object(
                Bucket=mock_aws_bucket_name,
                Key=file["key"],
                Body=f,
            )

    yield s3_client
