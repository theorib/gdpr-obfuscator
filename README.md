# GDPR Obfuscator

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Optional Requirements](#optional-requirements)
- [Installing and using GDPR Obfuscator in your python Project](#installing-and-using-gdpr-obfuscator-in-your-python-project)
  - [Installing with uv](#installing-with-uv)
  - [Installing with pip](#installing-with-pip)
  - [Using the GDPR Obfuscator package](#using-the-gdpr-obfuscator-package)
    - [Example: obfuscating a csv file](#example-obfuscating-a-csv-file)
    - [Example: Saving back to s3](#example-saving-back-to-s3)
- [Local Development and Testing](#local-development-and-testing)
  - [Requirements](#requirements-1)
  - [Optional Requirements](#optional-requirements-1)
  - [Installing uv](#installing-uv)
  - [Cloning this repository](#cloning-this-repository)
  - [Project Setup](#project-setup)
  - [Makefile commands](#makefile-commands)
  - [Deploying sample infrastructure into AWS](#deploying-sample-infrastructure-into-aws)


## Introduction
The purpose of this project is to create a general-purpose [Python](https://www.python.org) package that can process data stored on an AWS S3 bucket, obfuscating any personally identifiable information (PII) the data may contain. The generated result is an exact copy of the original data, but with the specified data fields replaced with obfuscated values such as `***`.

The package is designed to ingest data directly from a specified AWS S3 bucket. It returns a `bytes` object that can be easily stored back into a file on an S3 bucket or be further processed in the data pipeline. The package can be easily integrated into existing AWS services such as Lambda, Glue, Step Functions, EC2 instances, etc, being fully compatible with serverless environments.

It is written in [python](https://www.python.org), it is\ fully tested, PEP-8 compliant, and follows best practices for security and performance.

Currently the package supports ingesting and processing CSV files.

## Requirements
- Be confortable with the basics of running terminal commands using a [terminal emulator](https://en.wikipedia.org/wiki/Terminal_emulator) and have a terminal emulator installed in your computer.
- A basic understanding of [python](https://www.python.org).
- [Python](https://www.python.org) version 3.10 or higher installed and configured in your computer. If you haven't, you can install python using [uv](#installing-uv) or following the instructions on [installing python](https://www.python.org) manually.

## Optional Requirements
- We recommended [uv](https://docs.astral.sh/uv/) as your project's package manager. It can install python versions, create a virtual environment, and manage dependencies for you with no sweat.

## Installing and using GDPR Obfuscator in your python Project:

You can install and use **GDPR Obfuscator** in your project using any package manager. We recommend [uv](https://docs.astral.sh/uv/), but [pip](https://pypi.org/project/pip/) or any other modern package managers will work just as well.

You will have to set up your python project first before installing this package. We provide instructions for [uv](#installing-with-uv) and [pip](#installing-with-pip).

### Installing with [uv](https://docs.astral.sh/uv/)
If you haven't already, [install uv](#installing-uv) and on your terminal, navigate to the directory where you wish to create your python project. Run the following command and follow the onscreen prompts:
```bash
uv init
```
After you have initialized the project, add the **GDPR Obfuscator** as a dependency:

```bash
uv add git+https://github.com/theorib/gdpr-obfuscator.git
```

### Installing with [pip](#installing-with-pip)
On your terminal, navigate to the directory where you wish to create your python project and initialize your virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Then you can install the **GDPR Obfuscator** as a dependency:
```bash
pip install git+https://github.com/theorib/gdpr-obfuscator.git
```

### Using the **GDPR Obfuscator** package
`gdpr_obfuscator` takes two arguments:
- `file_to_obfuscate`: a `string`, formatted as an AWS s3 path `s3://bucket_name/file_key.csv` (keys with multiple directories are valid (`s3://bucket_name/directory_one/directory_two/file_key.csv`)).
- `pii_fields`: a `list` of `strings`, each representing a column or field that contains PII that should be obfuscated.

It returns a `bytes` object that is an exact copy of the original file, with the PII fields obfuscated. This object can then be saved back into a file and uploaded to s3 or be further processed on your data pipeline.

#### Example: obfuscating a csv file:
##### Code:
```python
from gdpr_obfuscator import gdpr_obfuscator

obfuscated_bytes = gdpr_obfuscator("s3://bucket_name/file_key.csv", ["name","email", "phone", "address"])
```

##### Input:
Consider a csv file with the following contents:
```csv
name,email,phone,address,department,position,company
John Doe,john.doe@example.com,123-456-7890,123 Main St,HR,Manager,Acme Corp
Jane Smith,jane.smith@example.com,987-654-3210,456 Elm St,IT,Developer,Acme Corp
```
##### Output:
The resulting csv would have all of the input's content with all fields passed to `pii_fields` obfuscated:
```csv
name,email,phone,address,department,position,company
***,***,***,***,HR,Manager,Acme Corp
***,***,***,***,IT,Developer,Acme Corp
```

#### Example: Saving back to s3
The result could be easily saved back to s3 using a library such as [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html):
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

## Local Development and Testing

You will need a [terminal emulator](https://en.wikipedia.org/wiki/Terminal_emulator) to run this project in a local development environment as well as [git](https://git-scm.com/downloads), [make](https://www.gnu.org/software/make/) and [uv](https://docs.astral.sh/uv/) installed. 
Additionally, to run sample infrastructure in AWS, you will need and AWS account setup and running, as well as the [aws cli](https://aws.amazon.com/cli/) installed and configured with your credentials. You will also need [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/) installed and configured with your AWS credentials.

Except for uv, Installing these tools is beyoud the scope of this project but you can find more information online or by following the outlined links. 

A terminal emulator comes builtin on MacOS and Linux, and can be easily installed on Windows using [Windows Terminal](https://docs.microsoft.com/en-us/windows/terminal/).

The commands you will see below can be copy/pasted into your terminal emulator. After pasting each command, press `Enter` to execute it.

### Requirements
- [uv](https://docs.astral.sh/uv/) is the package manager used in this project.
- [git](https://git-scm.com/downloads) to clone this repository 
- [make](https://www.gnu.org/software/make/) to run the makefile commands

### Optional Requirements
- [ruff](https://docs.astral.sh/ruff/) for code formatting and linting when developing locally and testing
- [aws cli](https://aws.amazon.com/cli/) for deploying sample infrastructure using this tool to AWS lambda when developing locally and testing
- [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/) for deploying sample infrastructure using this tool onto an AWS lambda function when developing locally and testing


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
This project contains Infrastructure as Code (IaC) scripts that can create sample infrastructure using the **GDPR Obfuscator** library  and deploy them to an AWS account using [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/).

The current pulumi setup has the capacity to:
- Create a sample s3 bucket
- Load the s3 bucket with test data.
- Create a sample lambda function that can read from that s3 bucket, and use the **GDPR Obfuscator** library to obfuscate data stored in the s3 bucket, saving the processed data back to s3.

#### To deploy the sample infrastructure, follow these steps:
Run all of the commands below from the root of your cloned repository.
1. Make sure you have followed the steps above for:
    - [Installing uv](#installing-uv)
    - [Cloning this repository](#cloning-this-repository)
    - [Project Setup](#project-setup)
2. Make sure you have the [Pulumi](https://www.pulumi.com/docs/iac/download-install/) CLI installed as well as the [aws cli](https://aws.amazon.com/cli/) installed and configured with your AWS credentials. 
3. Setup pulumi for this project:
    ```bash
    make sample-infrastructure-setup
    ```
4. Deploy sample infrastructure into your AWS account:
    ```bash
    make sample-infrastructure-deploy
    ```
    This will create a sample s3 bucket, load test data, and create a sample lambda function.

You can now login into your AWS Management Console and inspect the lambda and s3 buckets that were created as well as the sample data that was loaded into the bucket.

##### Running live tests with the sample infrastructure and GDPR Obfuscator
For convenience, we have provided a set of make scripts that you will run the lambda using the sample test files.

The following command will send a test event to the lambda function using a small sample test file.
```bash
make sample-infrastructure-run-test
```
The following script will send a test event with a large, 1MB csv test file containing 7031 data rows.
```bash
make sample-infrastructure-run-test-large
```
After running these scripts, you can check the output files that will have been saved within the same test buckets in the AWS management console. The file keys will be suffixed with `_obfuscated` before the extension (example: `large_pii_data_obfuscated.csv`).

Once you are done testing and want to clean up the AWS resources that were created, you can run:
```bash
make sample-infrastructure-destroy
```

##### Running manual tests on the sample infrastructure using the AWS management console

You can also manually test the lambda by giving it a test event of your choosing. Make sure it references an existing bucket as well as existing file keys and pii fields. If you want to manually use the sample bucket and test data provided, you can get their values by running:
```bash
make sample-infrastructure-get-output
```
The csv columns included in those files are the following. You can pick and choose any combination of them to obfuscate: 
```python
[
    "id", 
    "name", 
    "email_address", 
    "phone_number", 
    "date_of_birth", 
    "address", 
    "salary", 
    "department", 
    "hire_date", 
    "project_code", 
    "status", 
    "region"
]
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