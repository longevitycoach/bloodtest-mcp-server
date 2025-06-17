"""
Integration tests for the Blood Test Reference Values API with the existing workflow.
"""
import pytest
import json
from fastapi.testclient import TestClient
from bloodtest_tools.api import app
from bloodtest_tools.reference_values import get_reference_range, Sex

client = TestClient(app)

def test_bloodtest_api_integration():
    """Test the integration of the blood test API with the main application."""
    # Test 1: Verify the API root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "Blood Test Reference Values API" in data["name"]
    
    # Test 2: List all available parameters
    response = client.get("/parameters")
    assert response.status_code == 200
    data = response.json()
    assert "parameters" in data
    assert isinstance(data["parameters"], list)
    assert len(data["parameters"]) > 0
    
    # Test 3: Get reference range for a parameter (no sex)
    test_param = "ferritin"
    response = client.get(f"/reference/{test_param}")
    assert response.status_code == 200
    data = response.json()
    assert data["parameter"] == test_param
    assert "optimal_range" in data
    assert "classical_range" in data
    assert "explanation" in data
    
    # Test 4: Get reference range with sex parameter
    test_sex = "female"
    response = client.get(f"/reference/{test_param}?sex={test_sex}")
    assert response.status_code == 200
    data = response.json()
    assert data["parameter"] == test_param
    assert data["sex_specific"] is True
    assert data["sex_specific_range"] is not None
    
    # Test 5: Verify the reference values match the module's direct output
    module_result = get_reference_range(test_param, Sex[test_sex.upper()])
    assert data["optimal_range"] == module_result["optimal_range"]
    assert data["classical_range"] == module_result["classical_range"]
    
    # Test 6: Verify error handling for invalid parameter
    response = client.get("/reference/invalid_parameter")
    assert response.status_code == 404
    
    # Test 7: Verify error handling for invalid sex parameter
    response = client.get(f"/reference/{test_param}?sex=invalid_sex")
    assert response.status_code == 422  # Validation error

def test_bloodtest_api_with_workflow():
    """Test the blood test API in the context of a workflow."""
    # This is a simplified example of how the API might be used in a workflow
    
    # Simulate a blood test result
    blood_test_results = [
        {"parameter": "ferritin", "value": 85, "unit": "ng/ml"},
        {"parameter": "vitamin_d", "value": 45, "unit": "ng/ml"},
        {"parameter": "tsh", "value": 2.1, "unit": "mIU/l"}
    ]
    
    # Process each result using the API
    analysis_results = []
    for result in blood_test_results:
        param = result["parameter"]
        value = result["value"]
        
        # Get reference ranges
        response = client.get(f"/reference/{param}")
        if response.status_code == 200:
            ref_data = response.json()
            
            # Add analysis (simplified)
            analysis = {
                "parameter": param,
                "value": value,
                "unit": result["unit"],
                "optimal_range": ref_data["optimal_range"],
                "status": "normal"  # Simplified status determination
            }
            analysis_results.append(analysis)
    
    # Verify the analysis results
    assert len(analysis_results) == len(blood_test_results)
    for result in analysis_results:
        assert "optimal_range" in result
        assert result["status"] == "normal"  # In a real test, this would be more sophisticated
