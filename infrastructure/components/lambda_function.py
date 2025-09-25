"""Lambda function resources for GDPR obfuscation"""

import os

import pulumi
import pulumi_aws as aws


def create_lambda_function(
    lambda_role_arn,
    # test_data_bucket_id,
    # lambda_layer_bucket_id,
    lambda_name: str,
    project_root: str,
):
    """Create Lambda function for GDPR obfuscation processing"""

    lambda_function_file_path = os.path.join(project_root, f"src/{lambda_name}")
    lambda_layer_file_path = os.path.join(
        project_root, "dist/gdpr-obfuscator-layer.zip"
    )

    lambda_function_archive = pulumi.FileArchive(lambda_function_file_path)
    lambda_layer_archive = pulumi.FileArchive(lambda_layer_file_path)

    lambda_layer = aws.lambda_.LayerVersion(
        f"{lambda_name}-layer",
        layer_name=f"{lambda_name}-layer",
        code=lambda_layer_archive,
        compatible_runtimes=["python3.13"],
        # source_code_hash=
    )

    lambda_function = aws.lambda_.Function(
        lambda_name,
        role=lambda_role_arn,
        runtime="python3.13",
        handler=f"{lambda_name}.lambda_handler",
        code=lambda_function_archive,
        timeout=200,
        layers=[lambda_layer.arn],
    )


# return {
#     # "function": lambda_function,
# }
