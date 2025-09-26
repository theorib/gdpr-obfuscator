# GDPR Obfuscator

## Table of Contents

## Introduction
The purpose of this project is to create a general-purpose tool that can process data stored on an AWS S3 bucket obfuscating any personally identifiable information (PII) the data may contain. The generated result is an exact copy of the original data, but with the specified data fields replaced with obfuscated values such as `***`.

The tool is designed to ingest data directly from a specified AWS S3 bucket. It returns a `bytes` object that can be easily stored back into a file on an S3 bucket or be further processed in the data pipeline. The tool can be easily integrated into existing AWS services such as Lambda, Glue, Step Functions, EC2 instances, etc, being fully compatible with serverless environments.

It is written in [python](https://www.python.org), it's fully tested, PEP-8 compliant, and follows best practices for security and performance.

Currently the tool supports ingesting and processing CSV files.


## Requirements
- [python](https://www.python.org) 3.13 or higher
- [uv](https://docs.astral.sh/uv/) for building and running the project

## Optional Requirements
- [ruff](https://docs.astral.sh/ruff/) for code formatting and linting
- [aws cli](https://aws.amazon.com/cli/) for deploying sample infrastructure using this tool to AWS lambda
- [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/) for deploying sample infrastructure using this tool onto an AWS lambda function

## Installation Instructions

## Deploying sample infrastructure into AWS


install python
1. Install uv
2. uv sync
3. source into venv
4. export PYTHONPATH
- install ruff
- recommend install vscode ruff extension
- install aws cli
- configure aws cli
