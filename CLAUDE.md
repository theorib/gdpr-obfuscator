# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GDPR Obfuscator Project - a Python library for processing data ingested to AWS and intercepting personally identifiable information (PII). The tool obfuscates sensitive data in CSV, JSON, and Parquet files while maintaining data structure for bulk analysis.

**Context**: All information stored by Northcoders data projects should be for bulk data analysis only. Under GDPR requirements, all data containing information that can be used to identify an individual must be anonymized.

## Key Requirements

- **Input**: JSON string containing S3 location of data file (CSV, JSON, or Parquet) and field names to obfuscate
- **Output**: Bytestream representation compatible with boto3 S3 Put Object
- **Primary Use Case**: Library module for integration into Python codebases
- **Target Platform**: AWS ecosystem (EC2, ECS, Lambda)
- **Performance**: Handle files up to 1MB within 1 minute runtime
- **Data Format**: Data records will be supplied with a primary key
- **Invocation**: Expected to be invoked via EventBridge, Step Functions, or Airflow

## Development Standards

- **Language**: Python
- **Package Manager**: uv (<https://docs.astral.sh/uv/>)
- **Formatter & Linter**: ruff (<https://docs.astral.sh/ruff/>)
- **Testing**: Unit tested with pytest, including pytest-testdox and pytest-cov for test coverage, and Moto for AWS interaction testing
- **Code Quality**: PEP-8 compliant
- **Security**: Security vulnerability testing required
- **Documentation**: Code documentation required
- **Dependencies**: Complete module size must not exceed Python Lambda memory limits
- **Credentials**: No hardcoded credentials allowed

## Architecture

The project is now structured as a proper Python package with standard packaging conventions. All code interventions should respect this package structure and follow Python packaging best practices.

When implemented, it should follow these patterns:

- **Core Package**: Main obfuscation logic organized in `gdpr_obfuscator/` package directory
- **AWS Integration**: boto3 SDK integration within the package modules
- **CLI Interface**: Optional command-line interface accessible via package entry points
- **Library Interface**: Primary integration point through proper package imports and public API

## Example Usage Pattern

Input JSON:

```json
{
  "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
  "pii_fields": ["name", "email_address"],
  "file_type": "csv",
  "masking_string": "***"
}
```

Expected behavior: Replace sensitive data with obfuscated strings (default "***" or custom masking string) while preserving file structure and non-sensitive data. Supported file types: CSV, JSON, and Parquet.

## Git Commit Message Guidelines

Follow the Conventional Commits specification with gitmoji for all commits:

### Format

```
<emoji> <type>(<optional scope>): <description>

[optional body]

[optional footer]
```

### Subject Line Requirements

- Maximum 100 characters
- Use imperative mood (e.g., "add", "fix", "update")
- No capitalization of first letter
- No period at end
- Must be in English

### Recommended Types and Emojis

- ✨ `feat`: New feature
- 🐛 `fix`: Bug fix
- ♻️ `refactor`: Code restructuring without changing functionality
- 📝 `docs`: Documentation changes
- 🔧 `chore`: Maintenance tasks (dependencies, build tools)
- 🚀 `perf`: Performance improvements
- 🧪 `test`: Test-related changes
- 💄 `style`: Code style changes (formatting, missing semicolons)
- 🎨 `style`: Code structure improvements

### Body (Optional)

- Use bullet points with "-"
- Maximum 100 characters per line
- Explain "what" and "why", not "how"
- Use objective language

### Footer (Optional)

- Reference issues: `Fixes #123`
- Breaking changes: `BREAKING CHANGE: <description>`
- Co-authors: `Co-authored-by: Name <email>`

### Examples

```
✨ feat(obfuscator): add CSV field obfuscation functionality
🐛 fix(s3): handle missing bucket permissions gracefully
📝 docs: update API documentation for obfuscation methods
```

### Commit Strategy

- **Make small, incremental, atomic commits** - each commit should represent a single logical change
- Commit frequently to maintain clear evolution history and make debugging easier
- Each commit should be self-contained and not break the codebase
- Prefer multiple small commits over large monolithic commits
- This approach enables easier code review, rollback, and issue identification
- **Do NOT include "Co-Authored-By: Claude" in commit messages** - keep commits clean without AI attribution

## Development Commands

- **Install dependencies**: `uv sync`
- **Format code**: `uv run ruff format`
- **Lint code**: `uv run ruff check`
- **Run tests**: `uv run pytest`

## Implemented Features

- CSV, JSON, and Parquet file format support (output format same as input)
- Customizable masking strings for obfuscated data
- S3 integration for reading files from AWS buckets

## Future Extensions

- Enhanced obfuscation algorithms (e.g., hashing, tokenization)
- Support for nested JSON structures
- Batch processing of multiple files

## Project Timeline

- **Due Date**: Maximum four weeks from commencement

## Technical Specifications

- **AWS SDK**: Expected to use boto3 for S3 operations
- **Infrastructure as Code**: Pulumi for AWS infrastructure management and deployment automation
- **AWS Profile**: Always run `export AWS_PROFILE=AWS` before executing any Pulumi infrastructure commands
- **Testing Framework**: pytest with pytest-testdox and pytest-cov extensions, plus Moto for AWS service mocking
- **Deployment Compatibility**: EC2, ECS, or Lambda within AWS ecosystem
- **CLI Demo**: Optional command-line interface for demonstration purposes
