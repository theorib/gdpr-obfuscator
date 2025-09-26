#!/usr/bin/env python3
"""Standalone profiling script for GDPR obfuscator with minimal overhead."""

import os
from cProfile import Profile
from datetime import datetime
from pathlib import Path
from pstats import SortKey, Stats
from unittest.mock import MagicMock, patch

from src.gdpr_obfuscator.core.gdpr_obfuscator import gdpr_obfuscator


def main():
    """Profile GDPR obfuscator with lightweight aws s3 mocking."""

    # Test configuration
    test_file_path = "tests/data/large_pii_data.csv"
    expected_file_path = "tests/data/large_pii_data_obfuscated.csv"
    file_to_obfuscate = "s3://test-bucket/large_pii_data.csv"
    pii_fields = ["name", "email_address", "phone_number", "address"]
    profiling_data_output_path = "docs/profiling/standalone_profiling.prof"
    report_output_path = "docs/profiling/standalone_profiling.md"

    # Read test data
    with open(test_file_path, "rb") as f:
        test_file_data = f.read()

    # Read expected result for validation
    with open(expected_file_path, "rb") as f:
        expected = f.read()

    # Lightweight S3 mock
    mock_response = {"Body": MagicMock(), "ResponseMetadata": {"HTTPStatusCode": 200}}
    mock_response["Body"].read.return_value = test_file_data

    print("Starting profiling...")

    # Profiling
    with patch("boto3.client") as mock_boto_client:
        mock_s3_client = MagicMock()
        mock_s3_client.get_object.return_value = mock_response
        mock_boto_client.return_value = mock_s3_client

        with Profile() as profile:
            result = gdpr_obfuscator(file_to_obfuscate, pii_fields)

    # Validating result
    assert result == expected, "Obfuscated result doesn't match expected output"
    print("✅ Results validated")

    # Generate stats
    num_rows = (
        sum(1 for row in test_file_data.decode("utf-8").splitlines()) - 1
    )  # subtract 1 for the header_row
    stats = Stats(profile).strip_dirs()
    total_calls = stats.total_calls
    total_time = stats.total_tt
    prim_calls = stats.prim_calls

    # Save binary profile
    paren_dir = Path(profiling_data_output_path).parent
    os.makedirs(paren_dir, exist_ok=True)
    stats.sort_stats(SortKey.CALLS).dump_stats(profiling_data_output_path)

    _, data = generate_markdown_performance_report(
        total_time=total_time,
        total_calls=total_calls,
        primitive_calls=prim_calls,
        num_rows=num_rows,
        num_obfuscated_fields=len(pii_fields),
        source_file=__file__,
        profiling_data_output_path=profiling_data_output_path,
        report_output_path=report_output_path,
        additional_comments="Minimal overhead (no pytest, no moto, lightweight S3 mock)",
        methodology="""# Methodology
This measurement uses the leanest possible approach:
- Direct function call (no pytest overhead)
- Lightweight S3 mock (no moto/AWS SDK overhead)
- Validated correctness against expected output
- Pure core obfuscation logic performance""",
    )
    print("\n📊 Performance Results:")
    print(data)
    print(f"\n📄 Report saved to: {report_output_path}")
    print(f"🔍 Binary profile: {profiling_data_output_path}")


def generate_markdown_performance_report(
    total_time: float,
    total_calls: int,
    primitive_calls: int,
    num_rows: int,
    num_obfuscated_fields: int,
    source_file: str,
    profiling_data_output_path: str,
    report_output_path: str,
    additional_comments: str = "",
    methodology: str = "",
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = f"""- **Execution time**: {total_time:.6f} seconds
- **Function calls**: {total_calls:,} total ({primitive_calls:,} primitive calls)
- **Rows processed**: {num_rows:,}
- **Fields processed**: {num_rows * num_obfuscated_fields:,}
- **Throughput**: {num_rows / total_time:,.0f} rows/second
- **Data processed**: {num_rows:,.0f} rows with {num_obfuscated_fields} PII fields obfuscated
- **Additional comments**: {additional_comments}
"""

    report = f"""#GDPR Obfuscator Profiling Report
Generated: {timestamp}
Source: `{source_file}`

## Performance Summary
{data}

{methodology}

## Binary Profile
Detailed profiling data saved to: `{profiling_data_output_path}`

Load with: `python -c "import pstats; pstats.Stats('{profiling_data_output_path}').sort_stats('tottime').print_stats(20)"`
"""

    paren_dir = Path(report_output_path).parent
    os.makedirs(paren_dir, exist_ok=True)

    with open(report_output_path, "w") as f:
        f.write(report)

    return (report, data)


if __name__ == "__main__":
    main()
