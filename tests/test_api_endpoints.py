"""
Tests for the Blood Test Reference Values API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from bloodtest_tools.api import app

# Create a test client
client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data
    assert "GET /parameters" in data["endpoints"]
    assert "GET /reference/{parameter}" in data["endpoints"]

def test_list_parameters_endpoint():
    """Test the /parameters endpoint returns a list of available parameters."""
    response = client.get("/parameters")
    assert response.status_code == 200
    data = response.json()
    assert "parameters" in data
    assert isinstance(data["parameters"], list)
    assert len(data["parameters"]) > 0
    assert all("parameter" in p and "unit" in p for p in data["parameters"])

def test_get_reference_endpoint():
    """Test getting reference values for a parameter."""
    # Test with valid parameter
    response = client.get("/reference/ferritin")
    assert response.status_code == 200
    data = response.json()
    assert data["parameter"] == "ferritin"
    assert "optimal_range" in data
    assert "classical_range" in data
    assert "explanation" in data
    assert data["sex_specific"] is True

def test_get_reference_with_sex():
    """Test getting reference values with sex parameter."""
    # Test with female
    response = client.get("/reference/ferritin?sex=female")
    assert response.status_code == 200
    data = response.json()
    assert "premenopausal" in data.get("sex_specific_range", "").lower()

    # Test with male
    response = client.get("/reference/ferritin?sex=male")
    assert response.status_code == 200
    data = response.json()
    assert "30" in data.get("sex_specific_range", "")

def test_get_reference_invalid_parameter():
    """Test error handling for invalid parameter."""
    response = client.get("/reference/nonexistent_parameter")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_reference_invalid_sex():
    """Test error handling for invalid sex parameter."""
    response = client.get("/reference/ferritin?sex=invalid")
    assert response.status_code == 422  # Validation error
    assert "Input should be 'male' or 'female'" in response.text

def test_parameter_aliases():
    """Test that parameter aliases work correctly through the API."""
    aliases = ["vitamin d", "vitamind", "25-oh vitamin d"]
    for alias in aliases:
        response = client.get(f"/reference/{alias}")
        assert response.status_code == 200
        data = response.json()
        assert data["parameter"] == alias  # Should return the name as provided
        assert data["unit"] == "ng/ml"
