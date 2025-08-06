.PHONY: help install install-dev build test test-cov lint format format-check type-check security clean publish publish-test docs serve-docs all check

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package and dependencies"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  build        - Build distribution packages"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (ruff)"
	@echo "  format       - Format code (black + ruff)"
	@echo "  format-check - Check code formatting (black + ruff --check)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  clean        - Clean build artifacts"
	@echo "  publish      - Publish to PyPI"
	@echo "  publish-test - Publish to TestPyPI"
	@echo "  docs         - Build documentation"
	@echo "  serve-docs   - Serve documentation locally"
	@echo "  check        - Run all checks (lint, type-check, test)"
	@echo "  all          - Run full build pipeline"

# Installation
install:
	uv pip install -e .

install-dev:
	uv venv
	uv pip install -e ".[dev,docs]"

# Build
build: clean
	PIP_INDEX_URL=https://pypi.org/simple/ python3 -m build

# Testing
test:
	uv run pytest tests

test-cov:
	uv run pytest tests --cov=wrk_runner --cov-report=term-missing

# Code quality
lint:
	uv run ruff check src tests

format:
	uv run black src tests
	uv run ruff check --fix src tests

type-check:
	uv run mypy --ignore-missing-imports src

security:
	uv run bandit -r src
	uv run safety check

format-check:
	uv run black --check src tests
	uv run ruff check src tests

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Publishing
publish: build
	uv run twine upload dist/*

publish-test: build
	uv run twine upload --repository testpypi dist/*

# Documentation
docs:
	uv run mkdocs build

serve-docs:
	uv run mkdocs serve

# Combined targets
check: lint type-check test security

all: install-dev check build