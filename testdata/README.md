# Comprehensive Test Data for Bloodtest MCP Server

This directory contains comprehensive test data designed to validate all capabilities of the Bloodtest MCP Server. The test data is organized by functionality and covers both unit testing and integration testing scenarios.

## Directory Structure

### `/api_tests/`
Tests for the Blood Test Reference Values API
- Parameter lookup tests (all 8 supported parameters)
- Sex-specific range tests
- Parameter alias tests
- Error handling and edge cases
- Boundary value testing

### `/mcp_tool_tests/`
Tests for MCP protocol tools
- `get_book_info` tool tests
- `list_workflows` tool tests
- `supplement_therapy` workflow tests
- `sequential_thinking` tool tests
- `rag_search` tool tests

### `/blood_analysis_tests/`
Real-world blood test analysis scenarios
- Normal, abnormal, and borderline values
- Multiple patient demographics
- Various blood test formats
- German lab report formats (matching your system)
- Complex multi-parameter scenarios

### `/workflow_tests/`
Complete health coach workflow testing
- End-to-end supplement therapy scenarios
- Health assessment and goal setting
- Patient interaction patterns
- Personalized recommendation validation

### `/rag_tests/`
RAG (Retrieval-Augmented Generation) system tests
- Knowledge base queries
- Evidence-based recommendation tests
- Book citation verification
- Complex medical knowledge retrieval

### `/integration_tests/`
Full system integration scenarios
- Multi-tool coordination tests
- Complete patient journey tests
- Error handling across components
- Performance and reliability tests

## Supported Blood Test Parameters

The system supports these 8 parameters with optimal and classical reference ranges:

1. **Ferritin** (ng/ml) - Iron storage, sex-specific ranges
2. **TSH** (mIU/l) - Thyroid function
3. **Vitamin D** (ng/ml) - 25-OH Vitamin D
4. **Vitamin B12** (pmol/l) - Holotranscobalamin
5. **Folate RBC** (ng/ml) - Red blood cell folate
6. **Zinc** (mg/l) - Essential mineral
7. **Magnesium** (mmol/l) - Whole blood magnesium
8. **Selenium** (µg/l) - Antioxidant mineral

## Usage Instructions

### Running API Tests
```bash
# Test individual parameter lookup
curl "http://localhost:8000/reference/ferritin?sex=female"

# Test parameter listing
curl "http://localhost:8000/parameters"
```

### Running MCP Tool Tests
```bash
# Using the MCP client test script
python client_test.py
```

### Validation Criteria
Each test includes:
- **Input data**: Structured test inputs
- **Expected outputs**: Validation criteria
- **Success metrics**: Performance benchmarks
- **Error scenarios**: Expected error handling

## Test Data Formats

### API Test Format
```json
{
  "test_name": "parameter_lookup_test",
  "input": {"parameter": "ferritin", "sex": "female"},
  "expected": {"unit": "ng/ml", "contains": ["premenopausal"]},
  "validation": "response_structure_check"
}
```

### Blood Test Data Format
```json
{
  "patient_id": "test_001",
  "demographics": {"age": 35, "sex": "female"},
  "blood_results": [
    {"parameter": "ferritin", "value": 85, "unit": "ng/ml"},
    {"parameter": "vitamin_d", "value": 45, "unit": "ng/ml"}
  ],
  "expected_analysis": "deficiency_detected"
}
```

### Workflow Test Format
```json
{
  "scenario": "supplement_therapy_complete",
  "patient_context": {...},
  "expected_workflow": "personalized_plan_generation",
  "validation_points": [...]
}
```

## Contributing

When adding new test data:
1. Follow the established JSON structure
2. Include validation criteria
3. Add documentation for complex scenarios
4. Test with realistic data values
5. Include both positive and negative test cases

## Notes

- Test data includes German lab terminology to match real-world usage
- Patient data is anonymized and for testing purposes only
- Reference ranges are based on Dr. Strunz and Dr. Orfanos-Boeckel methodology
- All health recommendations are for educational testing purposes only
