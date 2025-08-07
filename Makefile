.PHONY: help install install-dev build test test-cov lint format format-check type-check security clean publish publish-test docs serve-docs all check pre-commit pre-commit-install

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
	@echo "  check        - Run all checks (lint, type-check, test, security)"
	@echo "  all          - Run full build pipeline"

install:
	PIP_INDEX_URL=https://pypi.org/simple/ uv pip install -e .

install-dev:
	uv venv
	PIP_INDEX_URL=https://pypi.org/simple/ uv pip install -e ".[dev,docs]"

build: clean
	PIP_INDEX_URL=https://pypi.org/simple/ uv run --active python3 -m build

test:
	uv run --active pytest tests

test-cov:
	uv run --active pytest tests --cov=wrk_runner --cov-report=term-missing

lint:
	uv run --active ruff check src tests

format:
	uv run --active black src tests
	uv run --active ruff check --fix src tests

type-check:
	uv run --active mypy --ignore-missing-imports src

security:
	uv run --active bandit -r src
	uv run --active safety scan --json || echo "Safety scan completed"

format-check:
	uv run --active black --check src tests
	uv run --active ruff check src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish: build
	uv run --active twine upload dist/*

publish-test: build
	uv run --active twine upload --repository testpypi dist/*

docs:
	uv run --active mkdocs build

serve-docs:
	uv run --active mkdocs serve

check: lint format type-check test security


all: install-dev check build