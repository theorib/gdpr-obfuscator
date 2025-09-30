##@ Utility
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make <target>\033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: uv
uv:  ## Install uv if it's not present
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	
.PHONY: sync
sync: uv ## Install dependencies
	@uv sync

.PHONY: build-lambda-layer
build-lambda-layer: sync ## Build AWS Lambda layer files without dependencies that are already included in the AWS Lambda environment
	rm -rf build
	mkdir -p build
	uv export --frozen --no-dev --no-editable --no-hashes | \
	grep -v "^\." | grep -v "^boto3=\|^botocore=\|^jmespath=\|^python-dateutil=\|^s3transfer=\|^six=\|^urllib3=" > build/lambda-requirements.txt

	mkdir -p build/layer/python
	uv pip install \
			--no-installer-metadata \
			--no-compile-bytecode \
			--python-platform x86_64-manylinux2014 \
			--python 3.13 \
			--target build/layer/python \
			-r build/lambda-requirements.txt
	uv pip install \
                --no-deps \
                --no-compile-bytecode \
                --target build/layer/python \
				.
	@echo "📄 Lambda layer requirements.txt created at: build/lambda-requirements.txt"
	@echo "📁 Lambda layer folder created at: build/layer/python"
	@echo "📏 Lambda layer unziped size: $$(du -sh build/layer/python | cut -f1)"

.PHONY: build-lambda-layer-zip
build-lambda-layer-zip: build-lambda-layer ## Create an AWS Lambda layer zip file without dependencies that are already included in the AWS Lambda environment
	mkdir -p dist
	cd build/layer && zip -r ../../dist/gdpr-obfuscator-layer.zip .
	@echo "📦 Lambda layer zip created at: dist/gdpr-obfuscator-layer.zip"
	@echo "📏 Lambda layer unzipped size: $$(du -sh build/layer/python | cut -f1)"
	@echo "🗜️  Lambda layer zipped size: $$(du -sh dist/gdpr-obfuscator-layer.zip | cut -f1)"
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
	uv run pytest --cov=src/gdpr_obfuscator --cov-report=term-missing

.PHONY: safe
safe: ## Run Bandit security scan
	uv run bandit -r -lll src

.PHONY: checks
checks: fix-all cov safe ## Run all checks

.PHONY: setup
setup: sync checks ## Runs all checks and instalation scripts to get your project running

STACK_NAME := dev
BUCKET_NAME = $(shell cd infrastructure && pulumi stack output bucket_name --stack $(STACK_NAME))
LAMBDA_FUNCTION_NAME = $(shell cd infrastructure && pulumi stack output lambda_function_name --stack $(STACK_NAME))
PII_DATA_KEY_COMPLEX = $(shell cd infrastructure && pulumi stack output pii_data_key_complex --stack $(STACK_NAME))
PII_DATA_KEY_LARGE = $(shell cd infrastructure && pulumi stack output pii_data_key_large --stack $(STACK_NAME))
PII_FIELDS=["name","email_address","phone_number","address"]

.PHONY: sample-infrastructure-setup
sample-infrastructure-setup: ## Set's up pulumi to be able to deploy sample infrastructure
	@echo "🚀 Setting up sample infrastructure"
	@echo "🔍 Checking AWS CLI setup..."
	@which aws >/dev/null 2>&1 || (echo "❌ AWS CLI not found. Please install it: https://aws.amazon.com/cli/" && exit 1)
	@echo "✅ AWS CLI found"
	@echo "🔐 Testing AWS credentials..."
	@aws sts get-caller-identity >/dev/null 2>&1 || (echo "❌ AWS credentials not configured or invalid. Run 'aws configure' to set them up." && exit 1)
	@echo "✅ AWS credentials working"
	@echo "🔍 Checking Pulumi CLI setup..."
	@which pulumi >/dev/null 2>&1 || (echo "❌ Pulumi CLI not found. Please install it: https://www.pulumi.com/docs/get-started/install/" && exit 1)
	@echo "✅ Pulumi CLI found"
	@cd infrastructure && pulumi login
	@cd infrastructure && (pulumi stack select $(STACK_NAME) 2>/dev/null || pulumi stack init $(STACK_NAME))
	@echo "📦 Installing Pulumi dependencies..."
	@cd infrastructure && uv sync
	@echo "✅ Sample infrastructure setup complete"

.PHONY: sample-infrastructure-clean-obfuscated-files
sample-infrastructure-clean-obfuscated-files: ## Cleans up any obfuscated sample files from the AWS sample bucket
	@echo "🧹 Cleaning obfuscated files from bucket: $(BUCKET_NAME)"
	@aws s3api list-objects-v2 --bucket $(BUCKET_NAME) --query "Contents[?contains(Key, 'obfuscated')].Key" --output text | \
	while read -r key; do \
		if [ -n "$$key" ] && [ "$$key" != "None" ]; then \
			echo "🗑️  Deleting: $$key"; \
			aws s3 rm "s3://$(BUCKET_NAME)/$$key"; \
		fi; \
	done
	@echo "✅ Cleanup complete"

.PHONY: sample-infrastructure-deploy
sample-infrastructure-deploy: build-lambda-layer-zip## Deploy the sample infrastructure to AWS
	@echo "🚀 Deploying sample infrastructure"
	@cd infrastructure && pulumi up --stack $(STACK_NAME) --yes
	@echo "✅ Sample infrastructure deployed"

.PHONY: sample-infrastructure-destroy
sample-infrastructure-destroy: sample-infrastructure-clean-obfuscated-files ## Destroy the sample infrastructure from AWS
	@echo "💥 Destroying sample infrastructure"
	@cd infrastructure && pulumi destroy --stack $(STACK_NAME) --yes
	@echo "✅ Sample infrastructure destroyed"

.PHONY: sample-infrastructure-run-test
sample-infrastructure-run-test: sample-infrastructure-clean-obfuscated-files ## Test the Lambda function with the complex PII data set
	@echo "🧪 Testing Lambda function: $(LAMBDA_FUNCTION_NAME)"
	@echo "🪣 Using bucket: $(BUCKET_NAME)"
	@echo "📄 Using complex PII data key: $(PII_DATA_KEY_COMPLEX)"
	@RESPONSE=$$(aws lambda invoke \
		--function-name $(LAMBDA_FUNCTION_NAME) \
		--payload '{"file_to_obfuscate":"s3://$(BUCKET_NAME)/$(PII_DATA_KEY_COMPLEX)","pii_fields":$(PII_FIELDS),"destination_bucket":"$(BUCKET_NAME)"}' \
		--cli-binary-format raw-in-base64-out \
		/dev/stdout 2>/dev/null); \
	if [ $$? -eq 0 ]; then \
		echo "$$RESPONSE" | jq .; \
		BODY=$$(echo "$$RESPONSE" | jq -r '.body // empty'); \
		if [ -n "$$BODY" ]; then \
			echo "✅ Lambda test completed successfully - obfuscated test file saved at: $$BODY"; \
		else \
			echo "✅ Lambda test completed successfully"; \
		fi; \
	else \
		echo "❌ Lambda test failed"; \
		exit 1; \
	fi

.PHONY: sample-infrastructure-run-test-large
sample-infrastructure-run-test-large: sample-infrastructure-clean-obfuscated-files ## Test the Lambda function with the large PII data set
	@echo "🧪 Testing Lambda function: $(LAMBDA_FUNCTION_NAME)"
	@echo "🪣 Using bucket: $(BUCKET_NAME)"
	@echo "📄 Using large PII data key: $(PII_DATA_KEY_LARGE)"
	@RESPONSE=$$(aws lambda invoke \
		--function-name $(LAMBDA_FUNCTION_NAME) \
		--payload '{"file_to_obfuscate":"s3://$(BUCKET_NAME)/$(PII_DATA_KEY_LARGE)","pii_fields":$(PII_FIELDS),"destination_bucket":"$(BUCKET_NAME)"}' \
		--cli-binary-format raw-in-base64-out \
		/dev/stdout 2>/dev/null); \
	if [ $$? -eq 0 ]; then \
		echo "$$RESPONSE" | jq .; \
		BODY=$$(echo "$$RESPONSE" | jq -r '.body // empty'); \
		if [ -n "$$BODY" ]; then \
			echo "✅ Lambda test completed successfully - obfuscated test file saved at: $$BODY"; \
		else \
			echo "✅ Lambda test completed successfully"; \
		fi; \
	else \
		echo "❌ Lambda test failed"; \
		exit 1; \
	fi

.PHONY: sample-infrastructure-get-data
sample-infrastructure-get-output: ## Get the obfuscated files
	@cd infrastructure && pulumi stack output --stack $(STACK_NAME)


