import logging
from pathlib import Path

import boto3

from gdpr_obfuscator import gdpr_obfuscator

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting lambda_handler", extra={"event": event})

    try:
        s3_client = boto3.client("s3")

        filename_base = Path(event["file_to_obfuscate"]).stem
        file_extension = Path(event["file_to_obfuscate"]).suffix

        result = gdpr_obfuscator(event["file_to_obfuscate"], event["pii_fields"])

        logger.info("Obfuscation complete", extra={"result": result})

        result_filename = f"{filename_base}_obfuscated{file_extension}"

        result_s3_address = f"s3://{event['destination_bucket']}/{result_filename}"

        response = s3_client.put_object(
            Bucket=event["destination_bucket"],
            Key=result_filename,
            Body=result,
            ContentType="text/csv",
        )

        logger.info("File uploaded to S3", extra={"response": response})

        result = {
            "statusCode": 200,
            "body": result_s3_address,
        }

        return result

    except Exception as e:
        logger.error(e)

        return {
            "statusCode": 500,
            "body": str(e),
        }
