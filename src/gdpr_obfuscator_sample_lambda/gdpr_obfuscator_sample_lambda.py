from pathlib import Path

import boto3

from gdpr_obfuscator import gdpr_obfuscator


def lambda_handler(event, context):
    s3_client = boto3.client("s3")

    filename_base = Path(event["file_to_obfuscate"]).stem
    file_extension = Path(event["file_to_obfuscate"]).suffix

    result = gdpr_obfuscator(event["file_to_obfuscate"], event["pii_fields"])

    result_filename = f"{filename_base}_obfuscated{file_extension}"

    result_s3_address = f"s3://{event['destination_bucket']}/{result_filename}"

    s3_client.put_object(
        Bucket=event["destination_bucket"],
        Key=result_filename,
        Body=result,
        ContentType="text/csv",
    )

    return {
        "statusCode": 200,
        "body": result_s3_address,
    }
