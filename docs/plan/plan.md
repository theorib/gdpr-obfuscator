# GDPR Obfuscator Project Plan

This file should be used as a living document for the development of this project. To do lists should be added, ticked and kept (or eventually modified when appropriate).

## Project Schedule

- Day 1: Planning, research and initial project setup
- Day 2: Start project implementation.

## Project Decisions to be made:

- [ ] Define Tech Stack
  - [ ] Use [Pydantic](https://docs.pydantic.dev/latest/) for Data Validation?
  - [ ] Use [Polars](https://pola.rs) to handle file manipulation?
  - [ ] which Python library to use to make creating cli applications easier?
  - [x] Use [bandit](https://bandit.readthedocs.io/en/latest/index.html) or [Semgrep](https://semgrep.dev) for static file-security analysis?
- [ ] Decide how to test and present the project specially AWS features?
  - [ ] Is docker a better alternative so I can more essily test lambdas locally?

## Project Setup todo list:

- [x] Install and setup [uv](https://docs.astral.sh/uv/)
- [x] Install and setup [ruff](https://docs.astral.sh/ruff/)
- [x] Install and set up [bandit](https://bandit.readthedocs.io/en/latest/index.html)
- [x] Install and set up [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/)
- [x] Install and set up [pytest](https://docs.pytest.org/en/stable/) with:
  - [x] pytest-testdox
  - [x] pytest-cov
- [x] Create test data
- [x] Create a make file with main project commands following the syntax and features proposed in [Makefile based on uv](https://mmngreco.dev/posts/uv-makefile/)
- [x] Setup [Moto](https://docs.getmoto.org/en/latest/docs/getting_started.html) for testing AWS interactions and setup fixtures that include the data to be ingested.
- [x] Setup [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
  - [x] Install and setup [mypy_boto3_builder](https://youtype.github.io/mypy_boto3_builder/)
  - [x] Install and set up [Type annotations for boto3](https://youtype.github.io/types_boto3_docs/)
- [ ] Find a time management app
- [x] Setup Bandit for static file-security analysis

## Testing

The project will use [pytest](https://docs.pytest.org/en/stable/) for testing with [pytest-testdox](https://pypi.org/project/pytest-testdox/) and [pytest-cov](https://pypi.org/project/pytest-cov/) for test coverage. It will also be using [Moto](https://docs.getmoto.org/en/latest/docs/getting_started.html) for testing AWS interactions.

## Project Structure

Current project structure (updated to reflect single package layout):

```
gdpr-obfuscator/
├── src/
│   └── gdpr_obfuscator/
│       ├── __init__.py
│       └── core/
│           ├── __init__.py
│           └── obfuscator.py
├── infrastructure/               # Standalone Pulumi project
│   ├── __main__.py
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── README.md
│   └── requirements.txt         # Infrastructure dependencies
├── tests/
│   └── __init__.py
├── docs/
│   └── plan/
│       └── plan.md
├── .env
├── .gitignore
├── .python-version
├── Makefile
├── pyproject.toml              # Main package configuration
├── README.md
└── uv.lock                     # Dependency lock file
```

**Key Changes:**

- Simplified from uv workspace to single package structure
- Infrastructure is now a standalone Pulumi project
- Source code organized under `src/gdpr_obfuscator/`
- Core obfuscation functionality implemented in `core/obfuscator.py`
- Tests directory prepared for unit and integration tests
