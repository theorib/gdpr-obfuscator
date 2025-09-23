"""Main obfuscation functionality for GDPR compliance."""

import io
from pprint import pprint
from typing import List, Tuple

import boto3
import polars as pl
from botocore.exceptions import ClientError


def gdpr_obfuscator(file_to_obfuscate: str, pii_fields: List[str]) -> bytes:
    """
    Obfuscate personally identifiable information (PII) fields in a CSV file.

    Args:
        file_to_obfuscate: S3 path to the CSV file (e.g., "s3://bucket_name/file_key.csv")
        pii_fields: List of column names containing PII to obfuscate

    Returns:
        A bytes object representing the obfuscated CSV file

    Raises:
        ValueError: If an empty file_to_obfuscate is passed
        FileNotFoundError: If the specified file doesn't exist (invalid s3 path)
        KeyError: If specified PII fields are not found in the CSV file
    """
    s3_client = boto3.client("s3")
    bucket, key = get_parse_s3_path(file_to_obfuscate)

    response = s3_client.get_object(Bucket=bucket, Key=key)
    # pprint(response)
    file = response["Body"].read()

    # Check if original file has trailing newline
    has_trailing_newline = file.endswith(b"\n")

    df = pl.read_csv(source=file)
    # print(df)
    df_obfuscated = df.with_columns([pl.lit("***").alias(col) for col in pii_fields])
    # print(df_obfuscated)

    buffer = io.BytesIO()
    df_obfuscated.write_csv(file=buffer)
    result = buffer.getvalue()

    # Match original file's trailing newline behavior
    if not has_trailing_newline and result.endswith(b"\n"):
        result = result[:-1]

    return result


def get_parse_s3_path(s3_path: str) -> Tuple[str, str]:
    prefix = "s3://"
    sanitized_s3_path = s3_path.strip()
    if not s3_path:
        raise FileNotFoundError("Invalid S3 path: Empty path string")
    if not sanitized_s3_path.startswith(prefix):
        raise FileNotFoundError('Invalid S3 path: Missing or malformed "s3://" prefix')

    base_string = sanitized_s3_path.strip().removeprefix(prefix)
    bucket_name = base_string.split("/")[0]
    key = base_string.removeprefix(bucket_name + "/")

    return bucket_name, key
