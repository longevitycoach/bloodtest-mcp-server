# API Tests for Blood Test Reference Values

This directory contains comprehensive tests for the Blood Test Reference Values API endpoints.

## Test Categories

### Parameter Lookup Tests
- `parameter_lookup_tests.json` - Tests for all 8 supported parameters
- `sex_specific_tests.json` - Tests for sex-specific reference ranges
- `parameter_alias_tests.json` - Tests for parameter name variations

### Error Handling Tests
- `error_handling_tests.json` - Invalid parameters, malformed requests
- `edge_case_tests.json` - Boundary conditions and special cases

### Validation Tests
- `response_structure_tests.json` - API response format validation
- `data_accuracy_tests.json` - Reference value accuracy verification

## Usage

These tests can be run using:
- Python `requests` library
- `curl` commands
- Automated test frameworks
- API testing tools (Postman, Insomnia)

## Test Data Format

Each test file contains an array of test cases with:
- `test_id`: Unique identifier
- `description`: Human-readable test description
- `endpoint`: API endpoint to test
- `method`: HTTP method (GET, POST, etc.)
- `input_data`: Request parameters
- `expected_response`: Expected response structure
- `validation_rules`: Criteria for success/failure
