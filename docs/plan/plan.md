# GDPR Obfuscator Project Plan

This file should be used as a living document for the development of this project. To do lists should be added, ticked and kept (or eventually modified when appropriate).

## Project Decisions to be made

- [x] Define Tech Stack
  - [x] Use [Pydantic](https://docs.pydantic.dev/latest/) for Data Validation? Respnse: No
  - [x] Use [Polars](https://pola.rs) to handle file manipulation?
  - [x] which Python library to use to make creating cli applications easier? Response: [Questionary](https://lyz-code.github.io/blue-book/questionary/)
  - [x] Use [bandit](https://bandit.readthedocs.io/en/latest/index.html) or [Semgrep](https://semgrep.dev) for static file-security analysis?
- [ ] Decide how to test and present the project specially AWS features?
  - [ ] Is docker a better alternative so I can more essily test lambdas locally?

## Project Setup todo list

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
- [x] Find a time management app ([clockify](http://clockify.me))
- [x] Setup Bandit for static file-security analysis

## Todo List

- [ ] Impplement character encoding matching for resulting csv files
- [ ] Implement line ending detection and maintain line endings
- [ ] implement json pretifying or not?
- [ ] Make sure dates retain the original format, metadata and compression
- [ ] Implement robust header matching for resulting csv files

## Other tests worth doing?

- [ ] General socket/connection errors
- [ ] ConnectionError
- [ ] ConnectionClosedError
- [ ] ReadTimeoutError
- [ ] EndpointConnectionError

- [ ] Service-side throttling/limit errors and exceptions
- [ ] Throttling
- [ ] ThrottlingException
- [ ] ThrottledException
- [ ] RequestThrottledException
- [ ] ProvisionedThroughputExceededException
