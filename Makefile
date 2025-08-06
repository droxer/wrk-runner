.PHONY: help install install-dev build test test-cov lint format type-check clean publish publish-test docs serve-docs all check

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
	uv pip install -e ".[dev,docs]"

# Build
build: clean
	PIP_INDEX_URL=https://pypi.org/simple/ python3 -m build

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=wrk_runner --cov-report=term-missing --cov-report=html --cov-report=xml

# Code quality
lint:
	uv run ruff check src tests

format:
	uv run black src tests
	uv run ruff check --fix src tests

type-check:
	uv run mypy --ignore-missing-imports src

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
check: lint type-check test

all: install-dev check build