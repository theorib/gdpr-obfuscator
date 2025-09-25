import pytest

from src.gdpr_obfuscator_sample_lambda.gdpr_obfuscator_sample_lambda import (
    lambda_handler,
)


@pytest.mark.describe("Test gdpr_obfuscateor_sample_lambda lambda_handler")
class TestGDPRObfuscatorLambdaHandler:
    # @pytest.mark.skip
    @pytest.mark.it("check that it saves an obfuscated version of the file to s3")
    def test_lambda_handler_returns_bytes(
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

        response = lambda_handler(
            event={
                "file_to_obfuscate": file_to_obfuscate,
                "pii_fields": pii_fields,
                "destination_bucket": mock_aws_bucket_name,
            },
            context={},
        )

        result = s3_client_with_files.get_object(
            Bucket=mock_aws_bucket_name,
            Key=test_files["csv"]["complex_pii_data"]["result_key"],
        )["Body"].read()

        assert result == expected

        assert response["statusCode"] == 200
