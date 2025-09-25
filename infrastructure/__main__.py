"""An AWS Python Pulumi program"""

import os

import pulumi
import pulumi_aws as aws
import pulumi_std as std

root = pulumi.get_root_directory()
project_root = os.path.abspath(os.path.dirname(root))


bucket = aws.s3.Bucket(
    "test-bucket",
    tags={
        "Project": "GDPR Obfuscator",
        "Environment": "Dev",
    },
)

complex_pii_data_path = os.path.join(project_root, "tests/data/complex_pii_data.csv")

test_data_complex_pii_data = aws.s3.BucketObject(
    "complex_pii_data",
    bucket=bucket.id,
    key="complex_pii_data.csv",
    source=pulumi.FileAsset(complex_pii_data_path),
    etag=std.filemd5(input=complex_pii_data_path).result,
)


pulumi.export("bucket_name", bucket.id)
pulumi.export("complex_pii_data_key", test_data_complex_pii_data.key)
