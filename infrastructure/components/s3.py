"""S3 bucket and object resources"""

import os

import pulumi
import pulumi_aws as aws
import pulumi_std as std


def create_test_buckets() -> dict[str, aws.s3.Bucket]:
    """Create S3 buckets and test data objects"""

    test_data_bucket = aws.s3.Bucket(
        "test-bucket",
        tags={
            "Project": "GDPR Obfuscator",
            "Environment": "Dev",
        },
    )

    return {
        "test_data_bucket": test_data_bucket,
    }


def create_test_data(project_root: str, bucket_name) -> dict[str, aws.s3.BucketObject]:
    complex_pii_data_path = os.path.join(
        project_root, "tests/data/complex_pii_data.csv"
    )
    large_pii_data_path = os.path.join(project_root, "tests/data/large_pii_data.csv")

    test_data_complex_pii_data = aws.s3.BucketObject(
        "complex_pii_data",
        bucket=bucket_name,
        key="complex_pii_data.csv",
        source=pulumi.FileAsset(complex_pii_data_path),
        etag=std.filemd5(input=complex_pii_data_path).result,
    )
    test_data_large_pii_data = aws.s3.BucketObject(
        "large_pii_data",
        bucket=bucket_name,
        key="large_pii_data.csv",
        source=pulumi.FileAsset(large_pii_data_path),
        etag=std.filemd5(input=large_pii_data_path).result,
    )

    return {
        "complex_pii_data": test_data_complex_pii_data,
        "large_pii_data": test_data_large_pii_data,
    }
