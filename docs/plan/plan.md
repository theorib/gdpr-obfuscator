# GDPR Obfuscator Project Plan

This file should be used as a living document for the development of this project. To do lists should be added, ticked and kept (or eventually modified when appropriate).

## Project Schedule

- Day 1: Planning, research and initial project setup
- Day 2:

## Project Setup todo list:

- [ ] Install and setup [uv](https://docs.astral.sh/uv/)
- [ ] Install and setup [ruff](https://docs.astral.sh/ruff/)
- [ ] Install and set up [bandit](https://bandit.readthedocs.io/en/latest/index.html)
- [ ] Install and set up [Pulumi](https://www.pulumi.com/product/infrastructure-as-code/)
- [ ] Install and set up [pytest](https://docs.pytest.org/en/stable/) with:
  - [ ] pytest-testdox
  - [ ] pytest-cov
- [ ] Create dummy data
- [ ] Define Tech Stack
- [ ] Create a make file with main project commands following the syntax and features proposed in [Makefile based on uv](https://mmngreco.dev/posts/uv-makefile/)
- [ ] Setup [Moto](https://docs.getmoto.org/en/latest/docs/getting_started.html) for testing AWS interactions and setup fixtures that include the data to be ingested.
- [ ] Decide how to test and present the project specially AWS features?
  - [ ] Is docker a better alternative so I can more essily test lambdas locally?
- [ ] Find a time management app

## Project Structure

Initial dummy project structure

```
gdpr-obfuscator/
├── src/
│   └── gdpr_obfuscator/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── obfuscator.py
│       │   └── processors/
│       ├── aws/
│       │   ├── __init__.py
│       │   └── s3_handler.py
│       └── cli/
│           ├── __init__.py
│           └── main.py
├── infrastructure/
│   ├── __main__.py
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.staging.yaml
│   ├── Pulumi.prod.yaml
│   ├── pyproject.toml          # Infrastructure-specific uv project
│   ├── uv.lock                 # Infrastructure lock file
│   └── modules/
│       ├── s3.py
│       ├── lambda.py
│       └── iam.py
├── .env
├── .gitignore
├── .python-version
├── tests/
├── docs/
├── Makefile
├── pyproject.toml              # Main application uv project
├── README.md
└── uv.lock                     # Main application lock file
```
