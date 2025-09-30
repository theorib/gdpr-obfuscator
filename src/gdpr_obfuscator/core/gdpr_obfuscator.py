"""Main obfuscation functionality for GDPR compliance."""

import io
from pathlib import Path
from typing import List, Literal, Tuple

import boto3
import polars as pl
from botocore.exceptions import ClientError
from types_boto3_s3.client import S3Client


def gdpr_obfuscator(
    file_to_obfuscate: str,
    pii_fields: List[str],
    masking_string: str = "***",
    file_type: Literal["csv", "json", "parquet"] = "csv",
) -> bytes:
    """
    Obfuscates personally identifiable information (PII) fields in CSV, JSON and Parquet files retrieved from an AWS S3 bucket.

    Args:
        file_to_obfuscate (str): S3 address to the file to be obfuscated. Formated as `s3://<bucket_name>/<file_key>` (e.g., "s3://my-bucket-name/some_file_to_obfuscate.csv")
        pii_fields (List[str]): List of column names containing PII to obfuscate (e.g. ["full_name", "date_of_birth", "address", "phone"])
        masking_string (str): String used to replace PII data (default is "***")
        file_type (Literal["csv", "json", "parquet"]): Type of file to obfuscate (default is "csv"), can be one of `csv`, `json`, or `parquet`

    Raises:
        ValueError: If an empty file_to_obfuscate is passed
        FileNotFoundError: If the specified file doesn't exist (invalid s3 path)
        KeyError: If specified PII fields are not found in the file
        RuntimeError: If an unexpected S3 response error occurs

    Returns:
        bytes: A bytes object representing the obfuscated CSV file
    """
    try:
        bucket, key = _parse_s3_path(file_to_obfuscate)
        s3_client = boto3.client("s3")  # type: ignore

        file = _get_file_from_s3(bucket, key, s3_client)

        has_trailing_newline = file.endswith(b"\n")

        if file_type == "csv":
            df = pl.read_csv(source=file)
        elif file_type == "json":
            df = pl.read_json(source=file)
        elif file_type == "parquet":
            df = pl.read_parquet(source=file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        missing_columns = [col for col in pii_fields if col not in df.columns]
        if missing_columns:
            raise KeyError(f"PII fields not found: {missing_columns}")

        df_obfuscated = df.with_columns([
            pl.lit(masking_string).alias(col) for col in pii_fields
        ])

        buffer = io.BytesIO()

        if file_type == "csv":
            df_obfuscated.write_csv(file=buffer)
            result = buffer.getvalue()

            if not has_trailing_newline and result.endswith(b"\n"):
                result = result[:-1]
        elif file_type == "json":
            df_obfuscated.write_json(file=buffer)
            result = buffer.getvalue()
        elif file_type == "parquet":
            df_obfuscated.write_parquet(file=buffer)
            result = buffer.getvalue()

        return result

    except pl.exceptions.NoDataError:
        raise ValueError("empty data from bytes")


def _parse_s3_path(s3_path: str) -> Tuple[str, str]:
    """Parses a given S3 path, such as "s3://bucket_name/file_key.csv" and returns an s3 bucket name and a file key

    Args:
        s3_path (str): an s3 path formatted as "s3://bucket_name/file_key.csv"

    Raises:
        FileNotFoundError: if an empty path string is given
        FileNotFoundError: if it has a malformed s3 path such as missing the "s3://" prefix

    Returns:
        Tuple[str, str]: a tuple containing the bucket name and the file key respectivelly
    """
    prefix = "s3://"
    sanitized_s3_path = s3_path.strip()
    if not s3_path:
        raise FileNotFoundError("Invalid S3 path: Empty path string")
    if not sanitized_s3_path.startswith(prefix):
        raise FileNotFoundError('Invalid S3 path: Missing or malformed "s3://" prefix')

    path = Path(sanitized_s3_path)

    bucket_name = path.parts[1]
    key = "/".join(path.parts[2:])

    return bucket_name, key


def _get_file_from_s3(bucket: str, key: str, s3_client: S3Client) -> bytes:
    """Retrieves a file from S3 and returns its contents as a bytes object

    Args:
        bucket (str): the name of the S3 bucket
        key (str): the key of the file in the S3 bucket
        s3_client (S3Client): the S3 client to use for the request

    Raises:
        RuntimeError: if the S3 response is not successful
        FileNotFoundError: if the specified key does not exist
        FileNotFoundError: if the specified bucket does not exist

    Returns:
        bytes: the contents of the file as a bytes object
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)

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

        return response["Body"].read()

    except ClientError as err:
        error_map = {
            "NoSuchKey": FileNotFoundError("The specified key does not exist."),
            "NoSuchBucket": FileNotFoundError("The specified bucket does not exist."),
        }
        # # print(err.response["Error"]["Code"])
        error_code = err.response.get("Error", {}).get("Code")
        if error_code in error_map:
            # print(err)
            raise error_map[error_code]
        else:
            raise err
