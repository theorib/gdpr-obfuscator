#!/usr/bin/env python3
"""Profiling script for GDPR obfuscator"""

import json
import os
import subprocess
from cProfile import Profile
from datetime import datetime
from pstats import SortKey, Stats
from typing import List, Literal
from unittest.mock import MagicMock, patch

import boto3
import polars as pl

from src.gdpr_obfuscator.core.gdpr_obfuscator import (
    _get_file_from_s3,
    _parse_s3_path,
    gdpr_obfuscator,
)


def get_stats_data(
    stats: Stats,
    original_bytes: bytes,
    file_type: Literal["csv", "json", "parquet"] = "csv",
):
    if file_type == "csv":
        df = pl.read_csv(source=original_bytes)
    elif file_type == "json":
        df = pl.read_json(source=original_bytes)
    elif file_type == "parquet":
        df = pl.read_parquet(source=original_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    num_rows = df.height
    total_calls = stats.total_calls  # type: ignore
    total_time = stats.total_tt  # type: ignore
    prim_calls = stats.prim_calls  # type: ignore

    return {
        "num_rows": num_rows,
        "total_calls": total_calls,
        "total_time": total_time,
        "prim_calls": prim_calls,
    }


def generate_markdown_performance_report(
    full_stats: Stats,
    mocked_stats: Stats,
    original_bytes: bytes,
    num_obfuscated_fields: int,
    source_file: str,
    profiling_data_output_dir: str,
    file_type: Literal["csv", "json", "parquet"] = "csv",
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract stats from both profiles
    full_data = get_stats_data(full_stats, original_bytes, file_type)
    mocked_data = get_stats_data(mocked_stats, original_bytes, file_type)

    # Calculate metrics
    num_rows = full_data["num_rows"]
    file_size_mb = len(original_bytes) / (1024 * 1024)

    full_time = full_data["total_time"]
    full_calls = full_data["total_calls"]
    full_prim_calls = full_data["prim_calls"]
    full_throughput = num_rows / full_time

    mocked_time = mocked_data["total_time"]
    mocked_calls = mocked_data["total_calls"]
    mocked_prim_calls = mocked_data["prim_calls"]
    mocked_throughput = num_rows / mocked_time

    # Calculate network overhead
    network_overhead = full_time - mocked_time
    network_overhead_pct = (network_overhead / full_time) * 100
    processing_time_pct = (mocked_time / full_time) * 100

    data_table = f"""| Metric | Full (S3 + Processing) | Mocked (Processing Only) | Difference |
|--------|------------------------|--------------------------|------------|
| **Execution Time** | {full_time:.6f}s | {mocked_time:.6f}s | {network_overhead:.6f}s ({network_overhead_pct:.1f}%) |
| **Throughput** | {full_throughput:,.0f} rows/s | {mocked_throughput:,.0f} rows/s | {mocked_throughput / full_throughput:.2f}x faster |
| **Function Calls** | {full_calls:,} | {mocked_calls:,} | +{full_calls - mocked_calls:,} |
| **Primitive Calls** | {full_prim_calls:,} | {mocked_prim_calls:,} | +{full_prim_calls - mocked_prim_calls:,} |

### Data Processed
- **File size**: {file_size_mb:.2f} MB
- **Rows**: {num_rows:,}
- **Fields obfuscated**: {num_obfuscated_fields}
- **Total fields processed**: {num_rows * num_obfuscated_fields:,}

### Key Insights
- **Network overhead**: {network_overhead:.6f}s ({network_overhead_pct:.1f}% of total time)
- **Processing time**: {mocked_time:.6f}s ({processing_time_pct:.1f}% of total time)
- **Speedup without network**: {mocked_throughput / full_throughput:.2f}x faster throughput
"""

    report = f"""# GDPR Obfuscator Profiling Report

**Generated**: {timestamp}
**Source**: `{source_file}`

## Performance Summary

{data_table}

## Profile Files

### Full Profile (S3 + Processing)
Complete end-to-end execution including S3 API calls and data processing.

**File**: `{profiling_data_output_dir}/full_profile.prof`

```bash
python -c "import pstats; pstats.Stats('{profiling_data_output_dir}/full_profile.prof').sort_stats('tottime').print_stats(20)"
```

### Mocked Profile (Processing Only)
Data obfuscation logic with S3 calls mocked (no network latency).

**File**: `{profiling_data_output_dir}/mocked_profile.prof`

```bash
python -c "import pstats; pstats.Stats('{profiling_data_output_dir}/mocked_profile.prof').sort_stats('tottime').print_stats(20)"
```

## Analysis

**Purpose**: Compare profiles to identify whether performance bottlenecks are network or algorithm related.

**Deployment optimization**: Running from EC2/Lambda in the same AWS region as the S3 bucket reduces network overhead.

**Scaling insights**: The mocked profile shows pure processing capacity independent of infrastructure.
"""

    os.makedirs(profiling_data_output_dir, exist_ok=True)
    report_output_path = f"{profiling_data_output_dir}/standalone_profiling.md"

    with open(report_output_path, "w") as f:
        f.write(report)

    return (report_output_path, data_table)


def get_pulumi_output():
    result = subprocess.run(
        ["pulumi", "stack", "output", "--stack", "dev", "-j"],
        capture_output=True,
        # text=True,
        check=True,
        cwd="infrastructure",
    )
    return json.loads(result.stdout)


def gdpr_obfuscator_profiling(
    file_to_obfuscate: str,
    pii_fields: List[str],
    profiling_data_output_dir: str,
    file_type: Literal["csv", "json", "parquet"] = "csv",
):
    """Profile GDPR obfuscator with and withoutlightweight aws s3 mocking."""
    bucket, key = _parse_s3_path(file_to_obfuscate)
    s3_client = boto3.client("s3")
    test_file_bytes = _get_file_from_s3(bucket, key, s3_client)

    print("Starting profiling...")

    with Profile() as full_profile:
        gdpr_obfuscator(file_to_obfuscate, pii_fields)

    # Lightweight S3 mock
    mock_response = {"Body": MagicMock(), "ResponseMetadata": {"HTTPStatusCode": 200}}
    mock_response["Body"].read.return_value = test_file_bytes

    # Profiling
    with patch("boto3.client") as mock_boto_client:
        mock_s3_client = MagicMock()
        mock_s3_client.get_object.return_value = mock_response
        mock_boto_client.return_value = mock_s3_client

        with Profile() as mocked_profile:
            gdpr_obfuscator(file_to_obfuscate, pii_fields)

    os.makedirs(profiling_data_output_dir, exist_ok=True)

    full_profile_file_name = "full_profile.prof"
    full_profile_output_path = os.path.join(
        profiling_data_output_dir, full_profile_file_name
    )
    full_stats = Stats(full_profile).strip_dirs()
    full_stats.sort_stats(SortKey.CALLS).dump_stats(full_profile_output_path)

    mocked_profile_file_name = "mocked_profile.prof"
    mocked_profile_output_path = os.path.join(
        profiling_data_output_dir, mocked_profile_file_name
    )
    mocked_stats = Stats(mocked_profile).strip_dirs()
    mocked_stats.sort_stats(SortKey.CALLS).dump_stats(mocked_profile_output_path)

    _, data = generate_markdown_performance_report(
        full_stats,
        mocked_stats,
        test_file_bytes,
        num_obfuscated_fields=len(pii_fields),
        source_file=__file__,
        profiling_data_output_dir=profiling_data_output_dir,
        file_type=file_type,
    )
    print("\n📊 Performance Results:")
    print(data)


def main():
    pulumi_output = get_pulumi_output()
    file_to_obfuscate = (
        f"s3://{pulumi_output['bucket_name']}/{pulumi_output['pii_data_key_large']}"
    )
    pii_fields = ["name", "email_address", "phone_number", "address"]
    profiling_data_output_dir = "profiling/"

    gdpr_obfuscator_profiling(
        file_to_obfuscate=file_to_obfuscate,
        pii_fields=pii_fields,
        profiling_data_output_dir=profiling_data_output_dir,
    )


if __name__ == "__main__":
    main()
