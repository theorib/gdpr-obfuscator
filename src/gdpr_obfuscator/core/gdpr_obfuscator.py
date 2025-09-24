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
        RuntimeError: If an unexpected S3 response error occurs
    """
    try:
        s3_client = boto3.client("s3")
        bucket, key = _get_parse_s3_path(file_to_obfuscate)

        response = s3_client.get_object(Bucket=bucket, Key=key)
        # pprint(response)

        if response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
            response_error_code = (
                response.get("ResponseMetadata").get("Error", {}).get("Code")
            )
            response_error_message = (
                response.get("ResponseMetadata").get("Error", {}).get("Message")
            )
            raise RuntimeError(
                f"Unexpected S3 response error. Error Code: {response_error_code}, Error Message: {response_error_message}"
            )

        file = response["Body"].read()

        has_trailing_newline = file.endswith(b"\n")

        df = pl.read_csv(source=file)

        missing_columns = [col for col in pii_fields if col not in df.columns]
        if missing_columns:
            raise KeyError(f"PII fields not found in CSV: {missing_columns}")

        df_obfuscated = df.with_columns([
            pl.lit("***").alias(col) for col in pii_fields
        ])
        # print(df)
        # print(df_obfuscated)

        buffer = io.BytesIO()
        df_obfuscated.write_csv(file=buffer)
        result = buffer.getvalue()

        if not has_trailing_newline and result.endswith(b"\n"):
            result = result[:-1]

        return result

    except pl.exceptions.NoDataError:
        raise ValueError("empty data from bytes")
    except ClientError as err:
        error_map = {
            "NoSuchKey": FileNotFoundError("The specified key does not exist."),
            "NoSuchBucket": FileNotFoundError("The specified bucket does not exist."),
        }
        # print(err.response["Error"]["Code"])
        error_code = err.response.get("Error", {}).get("Code")
        if error_code in error_map:
            # print(err)
            raise error_map[error_code]
        else:
            raise err


def _get_parse_s3_path(s3_path: str) -> Tuple[str, str]:
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
