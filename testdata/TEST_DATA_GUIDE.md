# Comprehensive Test Data Suite for Bloodtest MCP Server

This directory contains a complete test data suite designed to thoroughly validate all capabilities of your Bloodtest MCP Server. The test data covers API endpoints, MCP tools, RAG system, workflows, performance, error handling, and real-world scenarios.

## 📁 Test Data Files Overview

### Core Test Suites

1. **`comprehensive_api_tests.json`** - API endpoint testing
   - All 8 blood parameters (ferritin, TSH, vitamin D, B12, folate, zinc, magnesium, selenium)
   - Parameter aliases and variations
   - Sex-specific reference ranges
   - Error handling scenarios
   - Concurrent request testing

2. **`comprehensive_mcp_tool_tests.json`** - MCP protocol testing
   - `get_book_info` and `list_workflows` tools
   - `supplement_therapy` workflow execution
   - `sequential_thinking` multi-step reasoning
   - `search_book_knowledge` RAG integration
   - Error handling and edge cases

3. **`realistic_blood_analysis_scenarios.json`** - Patient scenarios
   - Young professional with fatigue (vegetarian, multiple deficiencies)
   - Active male with performance issues (athlete optimization)
   - Postmenopausal woman with bone health concerns
   - Edge cases: severe deficiencies, optimal values

4. **`comprehensive_rag_tests.json`** - Knowledge retrieval testing
   - Nutrient-specific searches (ferritin, vitamin D, magnesium forms)
   - Complex multi-nutrient interactions
   - Citation accuracy and source attribution
   - Performance benchmarks

5. **`comprehensive_workflow_tests.json`** - End-to-end workflows
   - Complete health assessment scenarios
   - Athletic performance optimization
   - Complex multi-deficiency cases
   - Integration error testing

6. **`comprehensive_integration_tests.json`** - System integration
   - Cross-component coordination
   - Data flow validation
   - Error cascade handling
   - Performance under load

### Advanced Test Suites

7. **`performance_load_tests.json`** - Performance validation
   - Response time benchmarks
   - Concurrent user simulation (10-200 users)
   - Memory and CPU monitoring
   - Stress testing and breaking points

8. **`error_handling_edge_cases.json`** - Error scenarios
   - Invalid parameters and malformed requests
   - Security injection attempts
   - System resource constraints
   - Recovery procedures

9. **`sample_blood_test_data.json`** - Realistic data samples
   - German lab report formats
   - Alternative terminology and units
   - Complex parsing challenges
   - Historical data and edge cases

### Test Utilities

10. **`test_runner.py`** - Automated test execution
    - Runs all test suites systematically
    - Generates comprehensive reports
    - Performance monitoring
    - Success/failure tracking

11. **`validate_test_data.py`** - Test data validation
    - Validates JSON structure and content
    - Checks parameter coverage
    - Ensures data consistency
    - Generates validation reports

## 🚀 Quick Start Guide

### 1. Validate Test Data
Before running tests, ensure all test data is valid:
```bash
cd /Users/ma3u/projects/Bloodtest-mcp-server/testdata
python validate_test_data.py
```

### 2. Start Your MCP Server
Ensure your server is running:
```bash
cd /Users/ma3u/projects/Bloodtest-mcp-server
python server.py --host 0.0.0.0 --port 8000
```

### 3. Run Comprehensive Tests
Execute the full test suite:
```bash
python test_runner.py
```

### 4. Review Results
Check the generated reports:
- `test_execution_results.json` - Detailed test results
- `validation_results.json` - Data validation results

## 📊 Test Coverage Analysis

### API Endpoints Coverage
- ✅ Health check (`/health`)
- ✅ Root endpoint (`/`)
- ✅ Parameter listing (`/parameters`)
- ✅ All 8 blood parameters (`/reference/{parameter}`)
- ✅ Sex-specific ranges (`?sex=male|female`)
- ✅ Error scenarios (404, 400, 405)

### MCP Tools Coverage
- ✅ `get_book_info` - System metadata
- ✅ `list_workflows` - Available workflows
- ✅ `supplement_therapy` - Main health coaching workflow
- ✅ `sequential_thinking` - Multi-step reasoning
- ✅ `search_book_knowledge` - RAG knowledge retrieval

### Blood Parameters Coverage
All 8 supported parameters with optimal vs classical ranges:
- ✅ **Ferritin** (ng/ml) - Iron storage with sex-specific ranges
- ✅ **TSH** (mIU/l) - Thyroid function
- ✅ **Vitamin D** (ng/ml) - 25-OH Vitamin D
- ✅ **Vitamin B12** (pmol/l) - Holotranscobalamin
- ✅ **Folate RBC** (ng/ml) - Red blood cell folate
- ✅ **Zinc** (mg/l) - Essential mineral
- ✅ **Magnesium** (mmol/l) - Whole blood magnesium
- ✅ **Selenium** (µg/l) - Antioxidant mineral

### Scenario Coverage
- ✅ Young adults with nutrient deficiencies
- ✅ Athletes seeking performance optimization
- ✅ Postmenopausal women with health concerns
- ✅ Vegetarians with specific nutritional needs
- ✅ Complex multi-deficiency cases
- ✅ Edge cases (severe deficiencies, optimal values)

## 🎯 Test Execution Strategies

### Development Testing
For daily development work:
```bash
# Quick API validation
python test_runner.py --suite api_only

# MCP tool validation  
python test_runner.py --suite mcp_only

# Single parameter testing
curl "http://localhost:8000/reference/ferritin?sex=female"
```

### Comprehensive Testing
Before releases or major changes:
```bash
# Full test suite
python test_runner.py

# Performance validation
python test_runner.py --suite performance

# Error handling validation
python test_runner.py --suite error_handling
```

### Load Testing
For production readiness:
```bash
# Simulate 50 concurrent users
python test_runner.py --load-test --users 50 --duration 300

# Stress test to breaking point
python test_runner.py --stress-test --max-users 200
```

## 📋 Test Data Structure Explained

### API Test Structure
```json
{
  "test_id": "api_001",
  "name": "descriptive_test_name", 
  "method": "GET",
  "endpoint": "/reference/ferritin",
  "query_params": {"sex": "female"},
  "expected_status": 200,
  "validation_rules": {
    "parameter": "ferritin",
    "sex_specific": true
  }
}
```

### Patient Scenario Structure
```json
{
  "patient_id": "test_patient_001",
  "demographics": {"age": 28, "sex": "female"},
  "presenting_symptoms": ["fatigue", "concentration issues"],
  "blood_test_results": {
    "parameters": [
      {"name": "ferritin", "value": 18, "unit": "ng/ml", "status": "low_normal"}
    ]
  },
  "expected_recommendations": {
    "priority_supplements": [...]
  }
}
```

### RAG Test Structure
```json
{
  "test_id": "rag_001", 
  "query": "optimal ferritin levels for women",
  "k": 5,
  "expected_content_themes": ["ferritin", "iron storage", "women"],
  "validation_criteria": {
    "min_relevance_score": 0.7,
    "must_contain_numeric_ranges": true
  }
}
```

## 🔧 Extending the Test Suite

### Adding New Test Cases

1. **New Blood Parameter**:
   - Add to `expected_parameters` in validation script
   - Create API tests in `comprehensive_api_tests.json`
   - Add reference ranges to your server's `reference_values.py`

2. **New Patient Scenario**:
   - Add to `realistic_blood_analysis_scenarios.json`
   - Include demographics, symptoms, blood results, expected recommendations
   - Ensure realistic and medically appropriate values

3. **New RAG Queries**:
   - Add to `comprehensive_rag_tests.json`
   - Include expected content themes and validation criteria
   - Test against your indexed medical books

### Customizing Test Parameters

1. **Performance Targets**:
   - Modify `baseline_performance_targets` in `performance_load_tests.json`
   - Adjust response time requirements based on your infrastructure

2. **Load Testing Limits**:
   - Increase `concurrent_users` for higher capacity testing
   - Adjust `test_duration_minutes` for longer stress tests

3. **Error Thresholds**:
   - Modify `error_rate_thresholds` in monitoring configuration
   - Customize `response_time_thresholds` for your SLA requirements

## 📈 Interpreting Test Results

### Success Metrics
- **API Tests**: 100% pass rate for core functionality
- **MCP Tests**: All tools respond correctly
- **RAG Tests**: Relevance scores > 0.7
- **Workflow Tests**: Complete scenario execution
- **Performance Tests**: Response times under targets

### Warning Indicators
- Response times approaching thresholds
- RAG relevance scores below 0.7
- Incomplete workflow executions
- Memory usage trends upward

### Failure Indicators
- API endpoints returning unexpected errors
- MCP tools timing out or failing
- RAG system unavailable
- Workflow crashes or incomplete results

## 🛠️ Troubleshooting Common Issues

### Server Not Responding
```bash
# Check server status
curl http://localhost:8000/health

# Verify port and host configuration
python server.py --host 0.0.0.0 --port 8000
```

### RAG System Issues
```bash
# Check FAISS index availability
ls -la faiss_index/

# Verify RAG configuration in structure.yaml
cat resources/structure.yaml | grep -A 5 "rag:"
```

### Test Data Validation Errors
```bash
# Run validation with detailed output
python validate_test_data.py --verbose

# Fix JSON formatting issues
python -m json.tool test_file.json
```

### Performance Issues
```bash
# Monitor system resources during tests
htop  # or top on macOS

# Check memory usage
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

## 📚 Additional Resources

### Related Documentation
- `README.md` - Server setup and configuration
- `HEALTH_LIFESTYLE_WORKFLOW.md` - Health coaching workflow details
- `requirements.txt` - Python dependencies

### Medical Reference Sources
The test data is based on optimal ranges from:
- Dr. Ulrich Strunz methodology
- Dr. Helena Orfanos-Boeckel "Naehrstoff-Therapie"
- Evidence-based functional medicine practices

### Test Data Sources
- Realistic German lab report formats
- Common blood chemistry panels
- Functional medicine optimization ranges
- Athletic performance monitoring parameters

---

## 🎉 Congratulations!

You now have a comprehensive test suite that validates every aspect of your Bloodtest MCP Server. This test data will help ensure your system provides accurate, safe, and effective personalized health recommendations.

**Next Steps:**
1. Run the validation script to confirm all test data is properly formatted
2. Execute the test runner to validate your server's functionality
3. Review results and address any issues found
4. Customize test parameters for your specific deployment requirements

For questions or issues with the test suite, review the troubleshooting section or examine the detailed validation results generated by the scripts.