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
        "parquet": {
            "complex_pii_data": {
                "local_path": "tests/data/complex_pii_data.parquet",
                "result_local_path": "tests/data/complex_pii_data_obfuscated.parquet",
                "key": "complex_pii_data.parquet",
                "result_key": "complex_pii_data_obfuscated.parquet",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
            "large_pii_data": {
                "local_path": "tests/data/large_pii_data.parquet",
                "result_local_path": "tests/data/large_pii_data_obfuscated.parquet",
                "key": "large_pii_data.parquet",
                "result_key": "large_pii_data_obfuscated.parquet",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
        },
        "json": {
            "complex_pii_data": {
                "local_path": "tests/data/complex_pii_data.json",
                "result_local_path": "tests/data/complex_pii_data_obfuscated.json",
                "key": "complex_pii_data.json",
                "result_key": "complex_pii_data_obfuscated.json",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
            "large_pii_data": {
                "local_path": "tests/data/large_pii_data.json",
                "result_local_path": "tests/data/large_pii_data_obfuscated.json",
                "key": "large_pii_data.json",
                "result_key": "large_pii_data_obfuscated.json",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
            "edge_cases_null_values": {
                "local_path": "tests/data/edge_cases_null_values.json",
                "result_local_path": "tests/data/edge_cases_null_values_obfuscated.json",
                "key": "edge_cases_null_values.json",
                "result_key": "edge_cases_null_values_obfuscated.json",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
        },
        "csv": {
            "simple_pii_data": {
                "local_path": "tests/data/simple_pii_data.csv",
                "result_local_path": "tests/data/simple_pii_data_obfuscated.csv",
                "key": "simple_pii_data.csv",
                "result_key": "simple_pii_data_obfuscated.csv",
                "pii_fields": ["email_address"],
            },
            "edge_cases_no_rows": {
                "local_path": "tests/data/edge_cases_no_rows.csv",
                "result_local_path": "tests/data/edge_cases_no_rows.csv",
                "key": "edge_cases_no_rows.csv",
                "result_key": "edge_cases_no_rows_obfuscated.csv",
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
            "large_pii_data": {
                "local_path": "tests/data/large_pii_data.csv",
                "result_local_path": "tests/data/large_pii_data_obfuscated.csv",
                "key": "large_pii_data.csv",
                "result_key": "large_pii_data_obfuscated.csv",
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
                "result_key": "edge_cases_non_standard_chars_obfuscated.csv",
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
                "result_key": "edge_cases_missing_data_obfuscated.csv",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
            "edge_cases_empty_file": {
                "local_path": "tests/data/edge_cases_empty_file.csv",
                "result_local_path": "tests/data/edge_cases_empty_file_obfuscated.csv",
                "key": "edge_cases_empty_file.csv",
                "result_key": "edge_cases_empty_file_obfuscated.csv",
                "pii_fields": [
                    "name",
                    "email_address",
                    "phone_number",
                    "address",
                ],
            },
            "simple_pii_data_different_masking_string": {
                "local_path": "tests/data/simple_pii_data_different_masking_string.csv",
                "result_local_path": "tests/data/simple_pii_data_different_masking_string_obfuscated.csv",
                "key": "simple_pii_data_different_masking_string.csv",
                "result_key": "simple_pii_data_different_masking_string_obfuscated.csv",
                "pii_fields": [
                    "email_address",
                ],
            },
        },
    }


@pytest.fixture(scope="class")
def get_test_file():
    def get_test_file_inner_factory(local_path: str) -> bytes:
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

    for key in test_files.keys():
        for file in test_files[key].values():
            with open(file["local_path"], mode="rb") as f:
                s3_client.put_object(
                    Bucket=mock_aws_bucket_name,
                    Key=file["key"],
                    Body=f,
                )

    yield s3_client
