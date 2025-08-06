.PHONY: help install install-dev build test test-cov lint format type-check clean publish publish-test docs serve-docs all check venv

# Default target
help:
	@echo "Available targets:"
	@echo "  venv         - Create and activate virtual environment"
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

# Virtual environment
venv:
	python3 -m venv venv
	@echo "Virtual environment created. Run 'source venv/bin/activate' to activate it."

# Installation
install:
	python3 -m pip install -e .

install-dev:
	python3 -m pip install -e ".[dev,docs]"

# Build
build: clean
	PIP_INDEX_URL=https://pypi.org/simple/ python3 -m build

# Testing
test:
	python3 -m pytest

test-cov:
	python3 -m pytest --cov=wrk_runner --cov-report=term-missing --cov-report=html --cov-report=xml

# Code quality
lint:
	python3 -m ruff check src tests

format:
	python3 -m black src tests
	python3 -m ruff check --fix src tests

type-check:
	python3 -m mypy --ignore-missing-imports src

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
	python -m twine upload dist/*

publish-test: build
	python -m twine upload --repository testpypi dist/*

# Documentation
docs:
	mkdocs build

serve-docs:
	mkdocs serve

# Combined targets
check: lint type-check test

all: install-dev check build