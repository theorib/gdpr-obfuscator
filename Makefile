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

.PHONY: test
test:  ## Run tests
	uv run pytest

.PHONY: test-main
test-main:  ## Run tests
	uv run pytest packages/gdpr-obfuscator/tests

.PHONY: lint
lint:  ## Run Ruff linter
	uv run ruff check ./packages/*/src ./packages/*/tests --fix

.PHONY: fmt
fmt:  ## Run Ruff formatter
	uv run ruff format --verbose ./packages/*/src ./packages/*/tests

.PHONY: fix
fix:  fmt lint ## Run Ruff linter and formatter

.PHONY: fix-all 
fix-all:  fmt lint ## Run Ruff linter and formatter

.PHONY: cov
cov: ## Run tests with coverage
	uv run pytest --cov=packages --cov-report=term-missing

.PHONY: safe
safe: ## Run Bandit security scan
	uv run bandit -r -lll packages/*/src

.PHONY: checks
checks: fix-all cov safe ## Run all checks

.PHONY: setup
setup: sync checks ## Runs all checks and instalation scripts to get your project running