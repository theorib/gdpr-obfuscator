# GDPR Obfuscator

## Table of Contents

- [GDPR Obfuscator](#gdpr-obfuscator)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Optional Requirements](#optional-requirements)
  - [Installing GDPR Obfuscator in your Python Project](#installing-gdpr-obfuscator-in-your-python-project)
    - [Installing with uv](#installing-with-uv)
    - [Installing with pip](#installing-with-pip)
  - [API Reference](#api-reference)
    - [`gdpr_obfuscator(file_to_obfuscate, pii_fields)`](#gdpr_obfuscatorfile_to_obfuscate-pii_fields)
      - [Parameters](#parameters)
      - [Raises](#raises)
      - [Returns](#returns)
    - [Examples](#examples)
      - [Obfuscating a CSV file](#obfuscating-a-csv-file)
      - [Obfuscating a Parquet file](#obfuscating-a-parquet-file)
      - [Obfuscating a JSON file with a custom masking string](#obfuscating-a-json-file-with-a-custom-masking-string)
      - [Saving back to S3](#saving-back-to-s3)
    - [Notes](#notes)
  - [Error Handling](#error-handling)
    - [Common Issues and Solutions](#common-issues-and-solutions)
      - [Malformed S3 Path](#malformed-s3-path)
      - [Invalid S3 Bucket](#invalid-s3-bucket)
      - [Invalid S3 Key](#invalid-s3-key)
      - [Missing PII Fields](#missing-pii-fields)
      - [File Format Issues](#file-format-issues)
  - [Performance](#performance)
    - [Performance Summary](#performance-summary)
      - [Data Processed](#data-processed)
      - [Key Insights](#key-insights)
  - [AWS Lambda Deployment Example](#aws-lambda-deployment-example)
  - [Local Development and Testing](#local-development-and-testing)
    - [Requirements](#requirements-1)
    - [Optional Requirements](#optional-requirements-1)
    - [Installing uv](#installing-uv)
    - [Cloning this repository](#cloning-this-repository)
    - [Makefile commands](#makefile-commands)
    - [Project Setup](#project-setup)
    - [Deploying sample infrastructure into AWS](#deploying-sample-infrastructure-into-aws)
      - [To deploy the sample infrastructure, follow these steps](#to-deploy-the-sample-infrastructure-follow-these-steps)
      - [Running live tests with the sample infrastructure and GDPR Obfuscator](#running-live-tests-with-the-sample-infrastructure-and-gdpr-obfuscator)
      - [Running manual tests on the sample infrastructure using the AWS management console](#running-manual-tests-on-the-sample-infrastructure-using-the-aws-management-console)
    - [Running performance tests locally](#running-performance-tests-locally)

## Introduction

The purpose of this project is to create a general-purpose [Python](https://www.python.org) package that can process data stored on an AWS S3 bucket, obfuscating any personally identifiable information (PII) the data may contain. The generated result is an exact copy of the original data, but with the specified data fields replaced with obfuscated values such as `***`.

The package is designed to ingest data directly from a specified AWS S3 bucket. It returns a `bytes` object that can be easily stored back into a file on an S3 bucket or be further processed in the data pipeline. The package can be easily integrated into existing AWS services such as Lambda, Glue, Step Functions, EC2 instances, etc, being fully compatible with serverless environments.

It is written in [Python](https://www.python.org), is fully tested using [pytest](https://docs.pytest.org/en/stable/), PEP-8 compliant (linted and formatted with [ruff](https://docs.astral.sh/ruff/)), and follows best practices for security and performance (tested using [bandit](https://bandit.readthedocs.io/en/latest/index.html)).

Currently the package supports ingesting and processing CSV, JSON, and Parquet files.

## Requirements

- Be comfortable with the basics of running terminal commands using a [terminal emulator](https://en.wikipedia.org/wiki/Terminal_emulator) and have a terminal emulator installed in your computer.
- A basic understanding of [Python](https://www.python.org).
- [Python](https://www.python.org) version 3.10 or higher installed and configured in your computer.

  This package has been tested with Python v3.10 through Python v3.13

  If you are using [uv](#installing-uv), you can install Python by running:

  ```bash
  uv python install
  ```

  Or by following their docs on [Installing Python](https://docs.astral.sh/uv/guides/install-python/).

  Otherwise, you can follow standard instructions on the Python official website to install it manually [installing Python](https://www.python.org).
- An active AWS account with appropriate credentials configured. This is required for anyone using this package as it reads data directly from an S3 bucket.

  The required IAM permissions depend on your use case:
  - **Minimum**: S3 read permissions (`s3:GetObject`) for the bucket(s) you'll be accessing
  - **Recommended**: Also include S3 write permissions (`s3:PutObject`) if you plan to save obfuscated results back to the same S3 bucket

  How you configure credentials depends on where you're running the package:
  - **Running locally**: Configure [AWS CLI](https://aws.amazon.com/cli/) with your access keys (see [Optional Requirements](#optional-requirements) below)
  - **Running on AWS (Lambda, EC2, ECS, etc)**: Use IAM roles attached to your compute resource

## Optional Requirements

- We recommend [uv](https://docs.astral.sh/uv/) as your project's package manager. It can install Python versions, create a virtual environment, and manage dependencies for you with no sweat.
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured with your AWS credentials. This is needed if you want to run this package locally on your computer for testing or development. Make sure your AWS CLI is configured with permissions that include S3 access to the bucket(s) you'll be working with. The AWS CLI is also required if you want to deploy the [sample Lambda infrastructure](#aws-lambda-deployment-example) included in this repository.

## Installing GDPR Obfuscator in your Python Project

You can install and use **GDPR Obfuscator** in your project using any package manager. We recommend [uv](https://docs.astral.sh/uv/), but [pip](https://pypi.org/project/pip/) or any other modern package managers will work just as well.

You will have to set up your Python project first before installing this package. We provide instructions for [uv](#installing-with-uv) and [pip](#installing-with-pip).

### Installing with [uv](https://docs.astral.sh/uv/)

If you haven't already, [install uv](#installing-uv) and on your terminal, navigate to the directory where you wish to create your Python project. Run the following command and follow the onscreen prompts:

```bash
uv init
```

After you have initialized the project, add the **GDPR Obfuscator** as a dependency:

```bash
uv add git+https://github.com/theorib/gdpr-obfuscator.git
```

### Installing with [pip](#installing-with-pip)

On your terminal, navigate to the directory where you wish to create your Python project and initialize your virtual environment:

```bash
python -m venv venv
source venv/bin/activate
export PYTHONPATH=$(pwd)
```

Then you can install the **GDPR Obfuscator** as a dependency:

```bash
pip install git+https://github.com/theorib/gdpr-obfuscator.git
```

## API Reference

### `gdpr_obfuscator(file_to_obfuscate, pii_fields)`

This is the main function that processes CSV, JSON, and Parquet files and obfuscates specified PII fields.

#### Parameters

- `file_to_obfuscate` (`str`): S3 address to the file to be obfuscated. Formatted as `s3://<bucket_name>/<file_key>` (e.g., `s3://my-bucket-name/some_file_to_obfuscate.csv`)
- `pii_fields` (`list[str]`): List of column names (or fields) that contain PII data to be obfuscated (e.g. `["full_name", "date_of_birth", "address", "phone"]`)
- `masking_string` (`str`): String used to replace PII data (default is `"***"`)
- `file_type` (`Literal["csv", "json", "parquet"]`): Type of file to obfuscate, can be one of `csv`, `json`, or `parquet`, (default is `"csv"`)

#### Raises

- `ValueError`: If an empty `file_to_obfuscate` is passed
- `FileNotFoundError`: If the specified file doesn't exist (invalid s3 path)
- `KeyError`: If any of the specified `pii_fields` are not found in the file
- `RuntimeError`: If an unexpected S3 response error occurs

#### Returns

- `bytes`: Obfuscated file as a `bytes` object, ready for S3 upload or further processing

### Examples

#### Obfuscating a CSV file

```python
from gdpr_obfuscator import gdpr_obfuscator

# Process a file with multiple PII fields
result = gdpr_obfuscator(
    "s3://my-bucket/customer-data.csv",
    ["email", "phone", "address"]
)
```

#### Obfuscating a Parquet file

```python
from gdpr_obfuscator import gdpr_obfuscator

result = gdpr_obfuscator(
    "s3://my-bucket/customer-data.parquet",
    ["email", "phone", "address"],
    file_type="parquet"
)
```

#### Obfuscating a JSON file with a custom masking string

```python
from gdpr_obfuscator import gdpr_obfuscator

result = gdpr_obfuscator(
    "s3://my-bucket/customer-data.json",
    ["email", "phone", "address"],
    masking_string="#######",
    file_type="json"
)
```

#### Saving back to S3

The result could be easily saved back to S3 using a library such as [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html):

```python
import boto3
from gdpr_obfuscator import gdpr_obfuscator

obfuscated_bytes = gdpr_obfuscator("s3://bucket-name/file_key.csv", ["name","email", "phone", "address"])

s3_client = boto3.client('s3')
 
response = s3_client.put_object(
    Bucket='another-bucket-name',
    Key='file_key_obfuscated.csv',
    Body=obfuscated_bytes,
    ContentType="text/csv", # specifying a MIME content type is optional
)
```

### Notes

- All PII field values are replaced with `***` by default but can be customized using the `masking_string` parameter
- Non-PII columns remain unchanged
- Original file structure and formatting is preserved
- Compatible with CSV, JSON, and Parquet files

## Error Handling

The GDPR Obfuscator handles common issues (see [Raises](#raises) above) and provides clear error messages.

### Common Issues and Solutions

#### Malformed S3 Path

- **Error:** `FileNotFoundError`
- **Error Message:** Invalid S3 path: Missing or malformed "s3://" prefix
- **Correct format:** `gdpr_obfuscator("s3://bucket-name/file.csv", ["field_1", "field_2"])`
- **Incorrect:** `gdpr_obfuscator("bucket/file.csv", ["field_1", "field_2"])`

#### Invalid S3 Bucket

- **Error:** `FileNotFoundError`
- **Error Message:** The specified key does not exist.
- **Solution:** Ensure the bucket name is correct and exists

#### Invalid S3 Key

- **Error:** `FileNotFoundError`
- **Error Message:** The specified key does not exist.
- **Solution:** Ensure the file key is correct and exists

#### Missing PII Fields

- **Error:** `KeyError`
- **Error Message:** `PII fields not found: ["Email"]`
- **Solution:** Check your CSV headers match the `pii_fields` exactly
- **Case-sensitive:** `"Email"` ≠ `"email"`

#### File Format Issues

- Only CSV, JSON, and Parquet files are currently supported
- CSV Files must have proper CSV headers in the first row
- JSON Files must have proper JSON structure
- Parquet Files must have proper Parquet structure
- Maximum file size: 1MB for optimal performance

## Performance

The GDPR Obfuscator is designed to handle large files efficiently. It can easily process files larger than 1MB with thousands of rows and is optimized for performance.

During local testing, the processing time for a large **1MB** csv file with **7,032 rows**, took 1.602619s.

99.8% of that time was spent with network overheads, (connecting to S3 and retrieving the data).

The actual time spent processing the data was only **0.003911s** (0.2% of total time).

You can [run performance tests locally](#running-performance-tests-locally) if you want

### Performance Summary

| Metric | Full (S3 + Processing) | Mocked (Processing Only) | Difference |
|--------|------------------------|--------------------------|------------|
| **Execution Time** | 1.602619s | 0.003911s | 1.598708s (99.8%) |
| **Throughput** | 4,388 rows/s | 1,797,872 rows/s | 409.74x faster |
| **Function Calls** | 26,852 | 491 | +26,361 |
| **Primitive Calls** | 25,113 | 489 | +24,624 |

#### Data Processed

- **File size**: 1.00 MB
- **Rows**: 7,032
- **Fields obfuscated**: 4
- **Total fields processed**: 28,128

#### Key Insights

- **Network overhead**: 1.598708s (99.8% of total time)
- **Processing time**: 0.003911s (0.2% of total time)
- **Speedup without network**: 409.74x faster throughput

## AWS Lambda Deployment Example

This repository includes a complete, production-ready example of deploying an AWS Lambda function that uses the GDPR Obfuscator package. It uses [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/) for infrastructure as code (a Python native package and CLI tool that is a modern alternative to [Terraform](https://terraform.io)).

The sample infrastructure demonstrates best practices for using this package on an AWS production environment, including:

- **Lambda Layers architecture**: The GDPR Obfuscator package and its dependencies are deployed as separate Lambda Layers, following AWS best practices for code organization and deployment
- **Proper IAM configuration**: Includes secure IAM roles and policies that follow the principle of least-privilege in order to give Lambda access to an S3 bucket with minimal permissions
- **S3 integration**: Sample S3 bucket with test data to help you get started quickly
- **CloudWatch logging**: Configured with JSON formatted logs for easy monitoring and debugging
- **Infrastructure as Code**: Everything is defined in Pulumi, making it easy to deploy, modify, and tear down

The Lambda function can be triggered manually or integrated with EventBridge, Step Functions, or other AWS services to create automated data obfuscation pipelines.

You can find detailed step-by-step instructions for deploying and testing the sample infrastructure in the [Deploying sample infrastructure into AWS](#deploying-sample-infrastructure-into-aws) section below.

This is a good reference implementation if you're planning to use the GDPR Obfuscator in your own AWS environment.

## Local Development and Testing

You will need a [terminal emulator](https://en.wikipedia.org/wiki/Terminal_emulator) to run this project in a local development environment as well as [git](https://git-scm.com/downloads), [make](https://www.gnu.org/software/make/) and [uv](https://docs.astral.sh/uv/) installed.
Additionally, to run sample infrastructure in AWS, you will need an AWS account setup and running, as well as the [aws cli](https://aws.amazon.com/cli/) installed and configured with your credentials. You will also need [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/) installed and configured with your AWS credentials.

Except for uv, installing these tools is beyond the scope of this project but you can find more information online or by following the outlined links.

A terminal emulator comes builtin on MacOS and Linux, and can be easily installed on Windows using [Windows Terminal](https://docs.microsoft.com/en-us/windows/terminal/).

The commands you will see below can be copy/pasted into your terminal emulator. After pasting each command, press `Enter` to execute it.

### Requirements

- [uv](https://docs.astral.sh/uv/) is the package manager used in this project.
- [git](https://git-scm.com/downloads) to clone this repository
- [make](https://www.gnu.org/software/make/) to run the makefile commands

### Optional Requirements

- [ruff](https://docs.astral.sh/ruff/) for code formatting and linting when developing locally and testing
- [AWS CLI](https://aws.amazon.com/cli/) for running this package locally or for deploying sample infrastructure into an AWS Lambda function
- [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/) for deploying sample infrastructure using this package onto an AWS lambda function when developing locally and testing

### Installing uv

uv is an extremely fast Python package and project manager, written in Rust. It is used to build and run this project.

If Python is already installed on your system, uv will detect and use it without configuration. However, if you don't have python installed, uv will automatically install missing Python versions as needed — you don't need to install Python to get started.

On MacOS or Linux, you can install uv with `curl` using:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On windows, run:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If you are running any different setup or are having issues installing uv, please refer to the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/) for more information.

### Cloning this repository

On your terminal, navigate to the directory where you want to install this project and clone this repository to your local machine using the following command:

```bash
git clone https://github.com/theorib/gdpr-obfuscator
```

### Makefile commands

We provide a series of Makefile commands to help you navigate this project. You can get a complete list of commands with a description of what they do by running:

```bash
make help
```

### Project Setup

Make sure uv and make are installed on your system and then from the root of your cloned project directory run:

```bash
make setup
```

This will install all dependencies and run checks to ensure everything is set up correctly. You should see all tests passing as well as security and test coverage reports in your terminal

### Deploying sample infrastructure into AWS

This project contains Infrastructure as Code (IaC) scripts using [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/), which is a modern Python-native alternative to [Terraform](https://developer.hashicorp.com/terraform).

It demonstrates a complete AWS deployment workflow using the **GDPR Obfuscator** package. It's a real-world example that follows AWS best practices and can serve as a reference for your own deployments.

The current pulumi setup is ready to:

- Create a sample S3 bucket
- Load the S3 bucket with test data
- Create a sample lambda function that can read from that S3 bucket, and use the **GDPR Obfuscator** package to obfuscate data stored in the S3 bucket, saving the processed data back to the same S3 bucket
- Configure proper IAM roles and policies following the principle of least privilege
- Set up CloudWatch logging for monitoring and debugging

#### To deploy the sample infrastructure, follow these steps

Run all of the commands below from the root of your cloned repository.

1. Make sure you have followed the steps above for:
    - [Installing uv](#installing-uv)
    - [Cloning this repository](#cloning-this-repository)
    - [Project Setup](#project-setup)
2. Make sure you have the [Pulumi](https://www.pulumi.com/docs/iac/download-install/) CLI installed and set up.
3. Make sure you have the [AWS CLI](https://aws.amazon.com/cli/) installed and configured with your AWS credentials.
4. Make sure that the user configured in the AWS CLI has the necessary permissions to create and manage resources in your AWS account.
5. Setup pulumi for this project:

    ```bash
    make sample-infrastructure-setup
    ```

6. Deploy sample infrastructure into your AWS account:

    ```bash
    make sample-infrastructure-deploy
    ```

    This will create a sample s3 bucket, load test data, and create a sample lambda function.

You can now login into your AWS Management Console and inspect the lambda and s3 buckets that were created as well as the sample data that was loaded into the bucket.

#### Running live tests with the sample infrastructure and GDPR Obfuscator

For convenience, we have provided a set of make scripts that will run the lambda using the sample test files.

The following command will send an event to the lambda function using a small sample test file.

```bash
make sample-infrastructure-run-test
```

The following script will send an event with a large, 1MB csv test file containing 7031 data rows.

```bash
make sample-infrastructure-run-test-large
```

After running these scripts, you can check the output files that will have been saved to the same test buckets in the AWS management console. The newly created file keys will be suffixed with `_obfuscated` before the extension (example: `large_pii_data_obfuscated.csv`).

Once you are done testing and want to clean up the AWS resources that were created, you can run:

```bash
make sample-infrastructure-destroy
```

#### Running manual tests on the sample infrastructure using the AWS management console

You can also manually test the lambda by giving it a test event of your choosing. Make sure it references an existing bucket as well as existing file keys and pii fields. If you want to manually use the sample bucket and test data provided, you can get their values by running:

```bash
make sample-infrastructure-get-output
```

The csv columns included in those files are the following. You can pick and choose any combination of them to obfuscate:

```python
["id", "name", "email_address", "phone_number", "date_of_birth", "address", "salary", "department", "hire_date", "project_code", "status", "region"]
```

The sample lambda, expects an event object as it's first argument and it should have the following shape:

```json
{
    "file_to_obfuscate": "s3://<bucket-name>/<file-key>",
    "pii_fields": [
        "field_1",
        "field_2",
        "field_3",
    ],
    "destination_bucket": "<bucket-name>"
}
```

Replace `<bucket-name>`,`<file-key>` and the `pii_fields` list with the values that you want (such as those from the `make sample-infrastructure-get-output` command). Or from any other bucket you may have that contains test data.

### Running performance tests locally

You can run performance tests locally for the `gdpr_obfuscator` function by using the make command:

```bash
make profile-gdpr-obfuscator
```

Make sure that before you do so, you have the [sample infrastructure deployed](#deploying-sample-infrastructure-into-aws)

Alternatively, you can import the `gdpr_obfuscator_profiling` function and run it directly with any suitable files you may have hosted on s3:

```python
from src.gdpr_obfuscator_profiling.gdpr_obfuscator_profiling import gdpr_obfuscator_profiling

gdpr_obfuscator_profiling(
  file_to_obfuscate="s3://some-bucket/some_file.parquet",
  pii_fields=["name", "email_address", "phone_number", "address"],
  profiling_data_output_dir='/profile-report',
  file_type="parquet"
)
```
