# Makefile for Blood Test MCP Server

# Variables
PYTHON = python
PIP = pip
DOCKER = docker
DOCKER_COMPOSE = docker-compose
VENV = .venv
PYTHON_VENV = $(VENV)/bin/python
PIP_VENV = $(VENV)/bin/pip

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	@echo "Blood Test MCP Server - Available commands:"
	@echo "  make setup        - Set up the development environment"
	@echo "  make install      - Install Python dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting and code style checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make run          - Run the application locally"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start services with Docker Compose"
	@echo "  make docker-down  - Stop services and remove containers"
	@echo "  make clean        - Clean up temporary files"

# Setup development environment
.PHONY: setup
setup:
	@echo "Setting up development environment..."
	$(PYTHON) -m venv $(VENV)
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements-dev.txt
	$(PIP_VENV) install -e .
	@echo "\nDevelopment environment ready! Activate it with 'source $(VENV)/bin/activate'"

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Run tests
.PHONY: test
test:
	$(PYTHON) -m pytest tests/ -v --cov=bloodtest_tools --cov-report=term-missing

# Run linting and code style checks
.PHONY: lint
lint:
	@echo "Running flake8..."
	$(PYTHON) -m flake8 bloodtest_tools tests
	@echo "\nRunning black..."
	$(PYTHON) -m black --check bloodtest_tools tests
	@echo "\nRunning isort..."
	$(PYTHON) -m isort --check-only bloodtest_tools tests

# Format code
.PHONY: format
format:
	$(PYTHON) -m black bloodtest_tools tests
	$(PYTHON) -m isort bloodtest_tools tests

# Run the application locally
.PHONY: run
run:
	$(PYTHON) -m uvicorn bloodtest_tools.api:app --reload

# Build Docker image
.PHONY: docker-build
docker-build:
	$(DOCKER) build -t bloodtest-mcp-server .

# Start services with Docker Compose
.PHONY: docker-up
docker-up:
	$(DOCKER_COMPOSE) up -d --build

# Stop services and remove containers
.PHONY: docker-down
docker-down:
	$(DOCKER_COMPOSE) down

# Clean up temporary files
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .coverage htmlcov/ build/ dist/

# Help target for listing all targets
.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | \
	awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | \
	sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
