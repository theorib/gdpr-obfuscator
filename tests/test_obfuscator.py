from curses import tigetflag

import pytest

from gdpr_obfuscator import gdpr_obfuscator


@pytest.mark.describe("Test the gdpr_obfuscator function")
class TestGDPRObfuscator:
    # @pytest.mark.skip
    @pytest.mark.it("check that it returns a bytes object")
    def test_function_returns_bytes(
        self, s3_client_with_files, mock_aws_bucket_name, test_files
    ):
        file_to_obfuscate = (
            f"s3://{mock_aws_bucket_name}/{test_files['csv']['sample_pii_data']['key']}"
        )
        pii_fields = ["name", "email"]

        result = gdpr_obfuscator(file_to_obfuscate, pii_fields)
        assert isinstance(result, bytes)

    @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with no rows, only the header, returns a copy of the original"
    )
    def test_csv_no_rows(self):
        pass

    @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with one matching column to be obfuscated returns a valid csv file with data from that column obfuscated"
    )
    def test_csv_with_matching_column(self):
        pass

    @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with multiple matching columns to be obfuscated returns a valid csv file with data from those columns obfuscated"
    )
    def test_csv_with_multiple_matching_columns(self):
        pass

    @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with non standard characters is processed correctly"
    )
    def test_csv_with_non_standard_characters(self):
        pass

    @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with missing data in some rows is processed correctly"
    )
    def test_csv_with_missing_data(self):
        pass

    @pytest.mark.skip
    @pytest.mark.it("check that an empty csv file raises a ValueError exception")
    def test_empty_csv_exception(self):
        pass

    @pytest.mark.skip
    @pytest.mark.it("check that an invalid s3 key raises a FileNotFoundError exception")
    def test_invalid_s3_key_exception(self):
        pass

    @pytest.mark.skip
    @pytest.mark.it(
        "check that a csv file with no matching columns to be obfuscated raises a KeyError exception"
    )
    def test_no_matching_columns(self):
        pass
