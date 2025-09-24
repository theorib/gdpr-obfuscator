##@ Utility
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make <target>\033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: uv
uv:  ## Install uv if it's not present
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	
.PHONY: sync
sync: uv ## Install dependencies
	uv sync

.PHONY: build-lambda-layer
build-lambda-layer: ## Build AWS Lambda layer files without dependencies that are already included in the AWS Lambda environment
	rm -rf build
	mkdir -p build
	uv export --frozen --no-dev --no-editable --no-hashes | \
	grep -v "^\.\|boto3\|botocore\|jmespath\|python-dateutil\|s3transfer\|six\|urllib3" > build/lambda-requirements.txt

	mkdir -p build/layer/python
	uv pip install \
			--no-installer-metadata \
			--no-compile-bytecode \
			--python-platform x86_64-manylinux2014 \
			--python 3.13.2 \
			--target build/layer/python \
			-r build/lambda-requirements.txt
	uv pip install \
                --no-deps \
                --no-compile-bytecode \
                --target build/layer/python \
				.
	@echo "Lambda layer requirements.txt created at: build/lambda-requirements.txt"
	@echo "Lambda layer folder created at: build/layer/python"
	@echo "Lambda layer unziped size: $$(du -sh build/layer/python | cut -f1)"

.PHONY: build-lambda-layer-zip
build-lambda-layer-zip: build-lambda-layer ## Create an AWS Lambda layer zip file without dependencies that are already included in the AWS Lambda environment
	mkdir -p dist
	cd build/layer && zip -r ../../dist/gdpr-obfuscator-layer.zip .
	@echo "**************"
	@echo "Lambda layer zip created at: dist/gdpr-obfuscator-layer.zip"
	@echo "Lambda layer unzipped size: $$(du -sh build/layer/python | cut -f1)"
	@echo "Lambda layer zipped size: $$(du -sh dist/gdpr-obfuscator-layer.zip | cut -f1)"
	@echo "**************"
	rm -rf build

.PHONY: test
test:  ## Run tests
	uv run pytest

.PHONY: lint
lint:  ## Run Ruff linter
	uv run ruff check ./src ./tests --fix

.PHONY: fmt
fmt:  ## Run Ruff formatter
	uv run ruff format --verbose ./src ./tests

.PHONY: fix
fix:  fmt lint ## Run Ruff linter and formatter

.PHONY: fix-all 
fix-all:  fmt lint ## Run Ruff linter and formatter

.PHONY: cov
cov: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=term-missing

.PHONY: safe
safe: ## Run Bandit security scan
	uv run bandit -r -lll src

.PHONY: checks
checks: fix-all cov safe ## Run all checks

.PHONY: setup
setup: sync checks ## Runs all checks and instalation scripts to get your project running