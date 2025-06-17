"""
Tests for the bloodtest_tools module.
"""
import pytest
from fastapi import HTTPException
from bloodtest_tools.reference_values import (
    get_reference_range,
    list_available_parameters,
    Sex
)
from bloodtest_tools.mcp_tool import BloodTestTool

def test_get_reference_range_valid_parameter():
    """Test getting reference range for a valid parameter."""
    # Test with no sex specified
    result = get_reference_range("ferritin")
    assert result["parameter"] == "ferritin"
    assert result["unit"] == "ng/ml"
    assert "70–200" in result["optimal_range"]
    assert result["sex_specific"] is True

    # Test with female
    result = get_reference_range("ferritin", Sex.FEMALE)
    assert "premenopausal" in result["sex_specific_range"].lower()

    # Test with male
    result = get_reference_range("ferritin", Sex.MALE)
    assert "30–400" in result["sex_specific_range"]

def test_get_reference_range_parameter_aliases():
    """Test that parameter aliases work correctly."""
    # Test different ways to refer to the same parameter
    param_names = ["vitamin d", "vitamind", "25-oh vitamin d", "25ohd"]
    for name in param_names:
        result = get_reference_range(name)
        assert result["parameter"] == name  # Should return the name as provided
        assert result["unit"] == "ng/ml"

def test_get_reference_range_invalid_parameter():
    """Test that an invalid parameter raises an error."""
    with pytest.raises(ValueError, match="not found in reference values"):
        get_reference_range("nonexistent_parameter")

def test_list_available_parameters():
    """Test that we can list all available parameters."""
    params = list_available_parameters()
    assert isinstance(params, list)
    assert len(params) > 0
    assert all(isinstance(p, dict) for p in params)
    assert all("parameter" in p and "unit" in p for p in params)

class TestBloodTestTool:
    """Tests for the BloodTestTool class."""
    
    def test_get_optimal_values_valid(self):
        """Test getting optimal values with valid parameters."""
        tool = BloodTestTool()
        
        # Test without sex
        result = tool.get_optimal_values("vitamin d")
        assert result["parameter"] == "vitamin d"
        assert result["unit"] == "ng/ml"
        
        # Test with female
        result = tool.get_optimal_values("ferritin", "female")
        assert "premenopausal" in result.get("sex_specific_range", "").lower()
        
        # Test with male
        result = tool.get_optimal_values("ferritin", "male")
        assert "30–400" in result.get("sex_specific_range", "")
    
    def test_get_optimal_values_invalid_sex(self):
        """Test with invalid sex parameter."""
        tool = BloodTestTool()
        with pytest.raises(HTTPException) as exc_info:
            tool.get_optimal_values("ferritin", "invalid_sex")
        assert exc_info.value.status_code == 400
        assert "Invalid sex" in str(exc_info.value.detail)
    
    def test_get_optimal_values_invalid_parameter(self):
        """Test with invalid parameter."""
        tool = BloodTestTool()
        with pytest.raises(HTTPException) as exc_info:
            tool.get_optimal_values("nonexistent_parameter")
        assert exc_info.value.status_code == 404
        
    def test_list_parameters(self):
        """Test listing available parameters."""
        tool = BloodTestTool()
        params = tool.list_parameters()
        assert isinstance(params, list)
        assert len(params) > 0
        assert all(isinstance(p, dict) for p in params)
        assert all("parameter" in p and "unit" in p for p in params)

def test_pydantic_models():
    """Test that Pydantic models can be instantiated correctly."""
    from bloodtest_tools.mcp_tool import (
        BloodTestParameterRequest,
        BloodTestParameterResponse,
        BloodTestParameterListResponse
    )
    
    # Test request model
    request = BloodTestParameterRequest(
        parameter="ferritin",
        sex="female"
    )
    assert request.parameter == "ferritin"
    assert request.sex == "female"
    
    # Test response model
    response = BloodTestParameterResponse(
        parameter="ferritin",
        unit="ng/ml",
        optimal_range="70-200",
        classical_range="15-400",
        explanation="Test explanation",
        sex_specific=True,
        sex_specific_range="15-150 (pre-menopausal)"
    )
    assert response.parameter == "ferritin"
    
    # Test list response model
    list_response = BloodTestParameterListResponse(
        parameters=[{"parameter": "ferritin", "unit": "ng/ml"}]
    )
    assert len(list_response.parameters) == 1
