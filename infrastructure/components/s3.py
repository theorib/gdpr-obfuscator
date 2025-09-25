"""S3 bucket and object resources"""

import os

import pulumi
import pulumi_aws as aws
import pulumi_std as std


def create_test_buckets(project_root: str):
    """Create S3 buckets and test data objects"""

    test_data_bucket = aws.s3.Bucket(
        "test-bucket",
        tags={
            "Project": "GDPR Obfuscator",
            "Environment": "Dev",
        },
    )

    lambda_layer_bucket = aws.s3.Bucket(
        "lambda-layer-bucket",
        tags={
            "Project": "GDPR Obfuscator",
            "Environment": "Dev",
        },
    )

    # Upload test data
    complex_pii_data_path = os.path.join(
        project_root, "tests/data/complex_pii_data.csv"
    )

    test_data_complex_pii_data = aws.s3.BucketObject(
        "complex_pii_data",
        bucket=test_data_bucket.id,
        key="complex_pii_data.csv",
        source=pulumi.FileAsset(complex_pii_data_path),
        etag=std.filemd5(input=complex_pii_data_path).result,
    )

    return {
        "test_data_bucket": test_data_bucket,
        "lambda_layer_bucket": lambda_layer_bucket,
        "test_data": test_data_complex_pii_data,
    }
