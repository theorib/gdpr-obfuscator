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
    )

    lambda_function = aws.lambda_.Function(
        lambda_name,
        role=lambda_role_arn,
        runtime="python3.13",
        handler=f"{lambda_name}.lambda_handler",
        code=lambda_function_archive,
        timeout=200,
        layers=[lambda_layer.arn],
        logging_config={
            "log_format": "JSON",
            "application_log_level": "INFO",
            "system_log_level": "WARN",
        },
        tags={
            "Project": "GDPR Obfuscator",
            "Environment": "Dev",
        },
    )

    log_group = aws.cloudwatch.LogGroup(
        f"{lambda_name}-log-group",
        name=lambda_function.name.apply(lambda name: f"/aws/lambda/{name}"),
        retention_in_days=1,
        tags={
            "Project": "GDPR Obfuscator",
            "Environment": "Dev",
        },
    )

    return {
        "lambda_function": lambda_function,
        "log_group": log_group,
    }
