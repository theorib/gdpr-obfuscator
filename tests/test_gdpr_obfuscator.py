from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ConnectionError
from moto import mock_aws

from src.gdpr_obfuscator.core.gdpr_obfuscator import gdpr_obfuscator
from src.gdpr_obfuscator.core.gdpr_obfuscator import _get_parse_s3_path


@pytest.mark.describe("Test the gdpr_obfuscator function")
@mock_aws
class TestGDPRObfuscator:
    # @pytest.mark.skip
    @pytest.mark.it("check that it returns a bytes object")
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
        assert result == expected

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
        expected = get_test_file(
            test_files["csv"]["simple_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)
        assert result == expected

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
        expected = get_test_file(
            test_files["csv"]["complex_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)
        assert result == expected

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
        expected = get_test_file(
            test_files["csv"]["complex_pii_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)
        assert result == expected

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
        expected = get_test_file(
            test_files["csv"]["edge_cases_non_standard_chars"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)
        assert result == expected

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
        expected = get_test_file(
            test_files["csv"]["edge_cases_missing_data"]["result_local_path"]
        )

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)
        assert result == expected

    # @pytest.mark.skip
    @pytest.mark.it("check that an empty file raises a ValueError exception")
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

    # @pytest.mark.skip
    @pytest.mark.it("check that an invalid s3 key raises a FileNotFoundError exception")
    def test_invalid_s3_key_exception(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://{mock_aws_bucket_name}/some_invalid_key.csv"
        pii_fields = ["name"]

        with pytest.raises(
            FileNotFoundError, match=r"The specified key does not exist."
        ):
            gdpr_obfuscator(file_to_obfuscate, pii_fields)

    # @pytest.mark.skip
    @pytest.mark.it("check that it raises an error if an invalid bucket name is passed")
    def test_invalid_bucket_name_exception(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        file_to_obfuscate = f"s3://some_invalid_bucket_name/{test_files['csv']['edge_cases_empty_file']['key']}"
        pii_fields = test_files["csv"]["edge_cases_empty_file"]["pii_fields"]

        with pytest.raises(
            FileNotFoundError, match=r"The specified bucket does not exist."
        ):
            gdpr_obfuscator(file_to_obfuscate, pii_fields)

    # @pytest.mark.skip
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

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that it raises an exception if there is a problem with the s3 connnection"
    )
    def test_s3_connection_error(
        self,
        s3_client_with_files,
        test_files,
        get_test_file,
        mock_aws_bucket_name,
    ):
        with patch("boto3.client") as mock_boto3_client:
            mock_s3 = mock_boto3_client.return_value
            mock_s3.get_object.side_effect = ConnectionError(error=Exception())

            file_to_obfuscate = f"s3://{mock_aws_bucket_name}/{test_files['csv']['edge_cases_no_rows']['key']}"
            pii_fields = ["name", "email_address"]

            with pytest.raises(ConnectionError):
                gdpr_obfuscator(file_to_obfuscate, pii_fields)

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that unexpected S3 response status codes raises a RuntimeError"
    )
    def test_unexpected_s3_response_status_code(
        self,
        s3_client_with_files,
        test_files,
    ):
        mock_response = {
            "ResponseMetadata": {
                "HTTPStatusCode": 500,
                "Error": {
                    "Code": "InternalError",
                    "Message": "We encountered an internal error. Please try again.",
                },
            },
            "Body": MagicMock(),
        }

        with patch("boto3.client") as mock_boto3:
            mock_s3_client = MagicMock()
            mock_s3_client.get_object.return_value = mock_response
            mock_boto3.return_value = mock_s3_client

            with pytest.raises(RuntimeError, match="Unexpected S3 response error"):
                gdpr_obfuscator("s3://test-bucket/test-file.csv", ["name"])


# !TODO Other tests todo:

# General socket/connection errors
# ConnectionError
# ConnectionClosedError
# ReadTimeoutError
# EndpointConnectionError

# Service-side throttling/limit errors and exceptions
# Throttling
# ThrottlingException
# ThrottledException
# RequestThrottledException
# ProvisionedThroughputExceededException


# test for partial reads with line count


@pytest.mark.describe("Test the get_parse_s3_path function")
class TestGetParseS3Pathget_parse_s3_path:
    # @pytest.mark.skip
    @pytest.mark.it(
        "check that a valid s3 path returns the correct bucket name and key"
    )
    def test_get_parse_s3_path(self):
        path = "s3://bucket_name/file_key.csv"
        bucket, key = _get_parse_s3_path(path)
        assert bucket == "bucket_name"
        assert key == "file_key.csv"

    # @pytest.mark.skip
    @pytest.mark.it("check that an invalid S3 path raises a FileNotFoundError exeption")
    def test_invalid_s3_path_exception(self):
        with pytest.raises(FileNotFoundError) as error:
            _get_parse_s3_path("bucket_name/file_key.csv")
        assert (
            str(error.value) == 'Invalid S3 path: Missing or malformed "s3://" prefix'
        )

    # @pytest.mark.skip
    @pytest.mark.it(
        "check that an empty path string returns a FileNotFoundError exception"
    )
    def test_empty_path_exception(self):
        with pytest.raises(FileNotFoundError) as error:
            _get_parse_s3_path("")
        assert str(error.value) == "Invalid S3 path: Empty path string"
