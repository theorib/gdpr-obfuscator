"""An AWS Python Pulumi program"""

import os

import pulumi
import pulumi_aws as aws
from components.iam import create_lambda_role, create_lambda_s3_policies
from components.lambda_function import create_lambda_function
from components.s3 import create_test_buckets

root = pulumi.get_root_directory()
project_root = os.path.abspath(os.path.dirname(root))

aws_region = aws.get_region().id
account_id = aws.get_caller_identity().account_id

test_lambda_name = "gdpr-obfuscator-test-lambda"

lambda_role = create_lambda_role(
    account_id=account_id, aws_region=aws_region, lambda_name=test_lambda_name
)


s3_resources = create_test_buckets(project_root)

lambda_test_bucket_s3_policies = create_lambda_s3_policies(
    lambda_role=lambda_role["lambda_role"],
    bucket_name=s3_resources["test_data_bucket"].id,
    bucket_arn=s3_resources["test_data_bucket"].arn,
    lambda_name=test_lambda_name,
)

lambda_layer_bucket_s3_policies = create_lambda_s3_policies(
    lambda_role=lambda_role["lambda_role"],
    bucket_name=s3_resources["lambda_layer_bucket"].id,
    bucket_arn=s3_resources["lambda_layer_bucket"].arn,
    lambda_name=test_lambda_name,
)


# lambda_resources = create_lambda_function(
#     lambda_role["lambda_role"].arn,
#     s3_resources["test_data_bucket"].id,
#     s3_resources["lambda_layer_bucket"].id,
# )


pulumi.export("bucket_name", s3_resources["test_data_bucket"].id)
pulumi.export("bucket_arn", s3_resources["test_data_bucket"].arn)
pulumi.export("complex_pii_data_key", s3_resources["test_data"].key)
pulumi.export("lambda_role_arn", lambda_role["lambda_role"].arn)
