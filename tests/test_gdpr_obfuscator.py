import io
from unittest.mock import MagicMock

import polars as pl
import pytest
from botocore.exceptions import ConnectionError
from moto import mock_aws

from src.gdpr_obfuscator.core.gdpr_obfuscator import (
    _get_file_from_s3,
    _parse_s3_path,
    gdpr_obfuscator,
)


@pytest.mark.describe("Test the gdpr_obfuscator function with CSV files")
@mock_aws
class TestGDPRObfuscatorCSV:
    # @pytest.mark.skip
    @pytest.mark.it("check that it returns a bytes object when passed a csv file")
    def test_function_returns_bytes(
        self,
        s3_client_with_files,
        mock_aws_bucket_name,
        test_files,
    ):
        file_to_obfuscate = (
            f"s3://{mock_aws_bucket_name}/{test_files['csv']['simple_pii_data']['key']}"
        )
        pii_fields = test_files["csv"]["simple_pii_data"]["pii_fields"]

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

        assert isinstance(result, bytes)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with no rows, only the header, returns a copy of the original"
    )
    def test_csv_no_rows(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['edge_cases_no_rows']['key']}"
        pii_fields = ["name", "email_address"]
        expected = get_test_file(test_files["csv"]["edge_cases_no_rows"]["local_path"])

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

        expected_df = pl.read_csv(io.BytesIO(expected))
        result_df = pl.read_csv(io.BytesIO(result))

        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with one matching column to be obfuscated returns a valid csv file with data from that column obfuscated"
    )
    def test_csv_with_matching_column(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = (
            f"s3://{mock_aws_bucket_name}/{test_files['csv']['simple_pii_data']['key']}"
        )
        pii_fields = test_files["csv"]["simple_pii_data"]["pii_fields"]
        expected_bytes = get_test_file(
            test_files["csv"]["simple_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

        expected_df = pl.read_csv(io.BytesIO(expected_bytes))
        result_df = pl.read_csv(io.BytesIO(result))

        assert isinstance(result, bytes)
        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with multiple matching columns to be obfuscated returns a valid csv file with data from those columns obfuscated"
    )
    def test_csv_with_multiple_matching_columns(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['complex_pii_data']['key']}"
        pii_fields = test_files["csv"]["complex_pii_data"]["pii_fields"]
        expected_bytes = get_test_file(
            test_files["csv"]["complex_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

        expected_df = pl.read_csv(io.BytesIO(expected_bytes))
        result_df = pl.read_csv(io.BytesIO(result))

        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that if the pii_fields columns are in a different order than the csv file that the obfuscation works and mantains the column order of the original file"
    )
    def test_column_order(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['complex_pii_data']['key']}"
        pii_fields = [
            "phone_number",
            "email_address",
            "name",
            "address",
        ]
        expected_bytes = get_test_file(
            test_files["csv"]["complex_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

        expected_df = pl.read_csv(io.BytesIO(expected_bytes))
        result_df = pl.read_csv(io.BytesIO(result))

        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with non standard characters is processed correctly"
    )
    def test_csv_with_non_standard_characters(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['edge_cases_non_standard_chars']['key']}"
        pii_fields = test_files["csv"]["edge_cases_non_standard_chars"]["pii_fields"]
        expected_bytes = get_test_file(
            test_files["csv"]["edge_cases_non_standard_chars"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

        expected_df = pl.read_csv(io.BytesIO(expected_bytes))
        result_df = pl.read_csv(io.BytesIO(result))

        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a different masking_string produces the expected result"
    )
    def test_different_masking_string(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['simple_pii_data_different_masking_string']['key']}"
        pii_fields = test_files["csv"]["simple_pii_data_different_masking_string"][
            "pii_fields"
        ]
        expected_bytes = get_test_file(
            test_files["csv"]["simple_pii_data_different_masking_string"][
                "result_local_path"
            ]
        )

        result = gdpr_obfuscator(
            file_to_obfuscate, pii_fields, masking_string="##########"
        )

        expected_df = pl.read_csv(io.BytesIO(expected_bytes))
        result_df = pl.read_csv(io.BytesIO(result))

        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with missing data in some rows is processed correctly"
    )
    def test_csv_with_missing_data(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['edge_cases_missing_data']['key']}"
        pii_fields = test_files["csv"]["edge_cases_missing_data"]["pii_fields"]
        expected_bytes = get_test_file(
            test_files["csv"]["edge_cases_missing_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

        expected_df = pl.read_csv(io.BytesIO(expected_bytes))
        result_df = pl.read_csv(io.BytesIO(result))

        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it("check that an empty csv file raises a ValueError exception")
    def test_empty_file_exception(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['edge_cases_empty_file']['key']}"
        pii_fields = test_files["csv"]["edge_cases_empty_file"]["pii_fields"]

        with pytest.raises(ValueError, match=r"empty data from bytes"):
            gdpr_obfuscator(file_to_obfuscate, pii_fields)

    @pytest.mark.it(
        "check that the file_to_obfuscate is formatted correctly, starting with s3://, otherwise raise a FileNotFoundError"
    )
    def test_file_to_obfuscate_format(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = (
            f"{mock_aws_bucket_name}/{test_files['csv']['simple_pii_data']['key']}"
        )
        pii_fields = test_files["csv"]["simple_pii_data"]["pii_fields"]

        with pytest.raises(
            FileNotFoundError,
            match=r'Invalid S3 path: Missing or malformed "s3://" prefix',
        ):
            gdpr_obfuscator(file_to_obfuscate, pii_fields)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with no matching columns to be obfuscated raises a KeyError exception"
    )
    def test_no_matching_columns(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = (
            f"s3://{mock_aws_bucket_name}/{test_files['csv']['simple_pii_data']['key']}"
        )
        pii_fields = ["nonexistent_column", "nonexistent_column_2"]

        with pytest.raises(
            KeyError,
            match=r'"PII fields not found in CSV: \[\'nonexistent_column\', \'nonexistent_column_2\'\]"',
        ):
            gdpr_obfuscator(file_to_obfuscate, pii_fields)


@pytest.mark.describe("Test the gdpr_obfuscator function with json files")
class TestGDPRObfuscatorJSON:
    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a json file with multiple matching columns to be obfuscated returns a valid json file with data from those columns obfuscated"
    )
    def test_json_multiple_matching_columns(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['json']['complex_pii_data']['key']}"
        pii_fields = test_files["json"]["complex_pii_data"]["pii_fields"]
        expected_bytes = get_test_file(
            test_files["json"]["complex_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields, file_type="json")

        expected_df = pl.read_json(io.BytesIO(expected_bytes))
        result_df = pl.read_json(io.BytesIO(result))

        assert isinstance(result, bytes)
        assert result_df.equals(expected_df)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a json file with random null values is processed correctly"
    )
    def test_json_random_null_values(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['json']['edge_cases_null_values']['key']}"
        pii_fields = test_files["json"]["edge_cases_null_values"]["pii_fields"]
        expected_bytes = get_test_file(
            test_files["json"]["edge_cases_null_values"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields, file_type="json")

        expected_df = pl.read_json(io.BytesIO(expected_bytes))
        result_df = pl.read_json(io.BytesIO(result))

        assert result_df.equals(expected_df)


@pytest.mark.describe("Test the gdpr_obfuscator function with parquet files")
class TestGDPRObfuscatorParquet:
    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a parquet file with multiple matching columns to be obfuscated returns a valid parquet file with data from those columns obfuscated"
    )
    def test_parquet_multiple_matching_columns(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['parquet']['complex_pii_data']['key']}"
        pii_fields = test_files["parquet"]["complex_pii_data"]["pii_fields"]
        expected_bytes = get_test_file(
            test_files["parquet"]["complex_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields, file_type="parquet")

        expected_df = pl.read_parquet(io.BytesIO(expected_bytes))
        result_df = pl.read_parquet(io.BytesIO(result))

        assert isinstance(result, bytes)
        assert result_df.equals(expected_df)


@pytest.mark.describe("Test _get_file_from_s3")
class TestGetFileFromS3:
    # @pytest.mark.skip
    @pytest.mark.it("check that it returns the expected bytes object")
    def test_get_file_from_s3_returns_bytes_object(
        self,
        s3_client_with_files,
        mock_aws_bucket_name,
        get_test_file,
        test_files,
    ):
        key = test_files["csv"]["complex_pii_data"]["key"]
        expected = get_test_file(test_files["csv"]["complex_pii_data"]["local_path"])

        result = _get_file_from_s3(mock_aws_bucket_name, key, s3_client_with_files)

        assert isinstance(result, bytes)
        assert result == expected

    # @pytest.mark.skip
    @pytest.mark.it("check that an invalid s3 key raises a FileNotFoundError exception")
    def test_get_file_from_s3_invalid_key(
        self,
        s3_client_with_files,
        mock_aws_bucket_name,
    ):
        key = "invalid_key"

        with pytest.raises(
            FileNotFoundError, match=r"The specified key does not exist."
        ):
            _get_file_from_s3(mock_aws_bucket_name, key, s3_client_with_files)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that it raises a FileNotFoundError exception if an invalid bucket name is passed "
    )
    def test_get_file_from_s3_invalid_bucket_name(
        self,
        s3_client_with_files,
    ):
        key = "test-file.csv"
        bucket_name = "invalid-bucket-name"
        with pytest.raises(
            FileNotFoundError, match=r"The specified bucket does not exist."
        ):
            _get_file_from_s3(bucket_name, key, s3_client_with_files)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that it raises a Connection Error if there is a problem with the s3 connection"
    )
    def test_get_file_from_s3_connection_error(
        self,
        mock_aws_bucket_name,
    ):
        s3_client = MagicMock()
        s3_client.get_object.side_effect = ConnectionError(error=Exception())
        key = "test-file.csv"
        with pytest.raises(ConnectionError):
            _get_file_from_s3(mock_aws_bucket_name, key, s3_client)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that an unexpected S3 response status codes raises a RuntimeError"
    )
    def test_get_file_from_s3_unexpected_status_code(self, mock_aws_bucket_name):
        s3_client = MagicMock()
        s3_client.get_object.return_value = {
            "ResponseMetadata": {
                "HTTPStatusCode": 500,
                "Error": {
                    "Code": "InternalError",
                    "Message": "We encountered an internal error. Please try again.",
                },
            },
            "Body": MagicMock(),
        }
        key = "test-file.csv"

        with pytest.raises(RuntimeError, match="Unexpected S3 response error"):
            _get_file_from_s3(mock_aws_bucket_name, key, s3_client)


@pytest.mark.describe("Test the get_parse_s3_path function")
class TestGetParseS3Pathget_parse_s3_path:
    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a valid s3 path returns the correct bucket name and key"
    )
    def test_get_parse_s3_path(self):
        path = "s3://bucket_name/file_key.csv"
        bucket, key = _parse_s3_path(path)

        assert bucket == "bucket_name"
        assert key == "file_key.csv"

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a path with a key with multiple nested directories returns the correct key"
    )
    def test_get_parse_s3_path_with_nested_directories(self):
        path = "s3://bucket_name/dir1/dir2/dir3/file_key.csv"
        bucket, key = _parse_s3_path(path)

        assert bucket == "bucket_name"
        assert key == "dir1/dir2/dir3/file_key.csv"

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a key with more than one file extension returns the correct key"
    )
    def test_key_with_multiple_extensions(self):
        path = "s3://bucket_name/file_key.csv.gz"
        bucket, key = _parse_s3_path(path)

        assert bucket == "bucket_name"
        assert key == "file_key.csv.gz"

    # @pytest.mark.skip
    @pytest.mark.it("check that an invalid S3 path raises a FileNotFoundError exeption")
    def test_invalid_s3_path_exception(self):
        with pytest.raises(FileNotFoundError) as error:
            _parse_s3_path("bucket_name/file_key.csv")

        assert (
            str(error.value) == 'Invalid S3 path: Missing or malformed "s3://" prefix'
        )

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that an empty path string returns a FileNotFoundError exception"
    )
    def test_empty_path_exception(self):
        with pytest.raises(FileNotFoundError) as error:
            _parse_s3_path("")

        assert str(error.value) == "Invalid S3 path: Empty path string"
