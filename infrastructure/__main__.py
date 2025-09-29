"""An AWS Python Pulumi program"""

import os

import pulumi
import pulumi_aws as aws
from components.iam import create_lambda_role, create_lambda_s3_policies
from components.lambda_function import create_lambda_function
from components.s3 import create_test_buckets, create_test_data

root = pulumi.get_root_directory()
project_root = os.path.abspath(os.path.dirname(root))

aws_region = aws.get_region().id
account_id = aws.get_caller_identity().account_id

test_lambda_name = "gdpr_obfuscator_sample_lambda"

lambda_role = create_lambda_role(
    account_id=account_id, aws_region=aws_region, lambda_name=test_lambda_name
)


s3_resources = create_test_buckets()

test_data = create_test_data(project_root, s3_resources["test_data_bucket"].id)

lambda_test_bucket_s3_policies = create_lambda_s3_policies(
    lambda_role_name=lambda_role["lambda_role"].name,
    bucket_name="test-data-bucket",
    bucket_arn=s3_resources["test_data_bucket"].arn.apply(lambda arn: f"{arn}/*"),  # type: ignore
    lambda_name=test_lambda_name,
)

lambda_layer_bucket_s3_policies = create_lambda_s3_policies(
    lambda_role_name=lambda_role["lambda_role"].name,
    bucket_name="lambda-layer-bucket",
    bucket_arn=s3_resources["lambda_layer_bucket"].arn.apply(lambda arn: f"{arn}/*"),  # type: ignore
    lambda_name=test_lambda_name,
)


lambda_function = create_lambda_function(
    lambda_role_arn=lambda_role["lambda_role"].arn,
    lambda_name=test_lambda_name,
    project_root=project_root,
)


pulumi.export("bucket_name", s3_resources["test_data_bucket"].id)
pulumi.export("bucket_arn", s3_resources["test_data_bucket"].arn)
pulumi.export("pii_data_key_complex", test_data["complex_pii_data"].key)
pulumi.export("pii_data_key_large", test_data["large_pii_data"].key)
pulumi.export("lambda_role_arn", lambda_role["lambda_role"].arn)
pulumi.export("lambda_function_arn", lambda_function["lambda_function"].arn)
pulumi.export("lambda_function_name", lambda_function["lambda_function"].name)
