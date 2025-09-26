# GDPR Obfuscator

## Table of Contents

## Introduction
The purpose of this project is to create a general-purpose tool that can process data stored on an AWS S3 bucket obfuscating any personally identifiable information (PII) the data may contain. The generated result is an exact copy of the original data, but with the specified data fields replaced with obfuscated values such as `***`.

The tool is designed to ingest data directly from a specified AWS S3 bucket. It returns a `bytes` object that can be easily stored back into a file on an S3 bucket or be further processed in the data pipeline. The tool can be easily integrated into existing AWS services such as Lambda, Glue, Step Functions, EC2 instances, etc, being fully compatible with serverless environments.

It is written in [python](https://www.python.org), it's fully tested, PEP-8 compliant, and follows best practices for security and performance.

Currently the tool supports ingesting and processing CSV files.


## Requirements
- [uv](https://docs.astral.sh/uv/) for building and running the project
    - [python](https://www.python.org) 3.13 or higher

## Optional Requirements
- [ruff](https://docs.astral.sh/ruff/) for code formatting and linting
- [aws cli](https://aws.amazon.com/cli/) for deploying sample infrastructure using this tool to AWS lambda
- [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/) for deploying sample infrastructure using this tool onto an AWS lambda function

## Installation Instructions

You will need a terminal emulator to run this project as well as [git](https://git-scm.com/downloads) and [make](https://www.gnu.org/software/make/). Installing these tools is beyoud the scope of this project but you can find more information online or on the links above. 

A terminal emulator comes builtin on MacOS and Linux, and can be easily installed on Windows using [Windows Terminal](https://docs.microsoft.com/en-us/windows/terminal/). Installing a terminal emulator is required but beyoud the scope of this project.

The commands you will see below can be copy/pasted into your terminal emulator. After pasting each command, press `Enter` to execute it.

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
On yout terminal, navigate to the directory where you want to install this project and clone this repository to your local machine using the following command:

```bash
git clone https://github.com/theorib/gdpr-obfuscator
```

### Project Setup

To get this project up and running, from the root of the project directory run:

```bash
make setup
```

This will install all dependencies and run checks to ensure everything is set up correctly.

### Makefile commands
We provide a series of Makefile commands to help you navigate this project. You can get a complete list of commands with a description of what they do by running:

```bash
make help
```

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
