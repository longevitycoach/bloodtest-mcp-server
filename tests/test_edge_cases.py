"""
Edge case tests for the Blood Test Reference Values API and tools.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from bloodtest_tools.api import app
from bloodtest_tools.mcp_tool import BloodTestTool
from bloodtest_tools.reference_values import get_reference_range, Sex

client = TestClient(app)

def test_empty_parameter_string():
    """Test behavior with empty parameter strings."""
    # Test with empty string
    with pytest.raises(ValueError):
        get_reference_range("")
    
    # Test with whitespace-only string
    with pytest.raises(ValueError):
        get_reference_range("   ")
    
    # Test with API
    response = client.get("/reference/")
    assert response.status_code == 404  # Not found, as empty parameter is not a valid route

def test_long_parameter_name():
    """Test with very long parameter names."""
    long_param = "a" * 1000
    with pytest.raises(ValueError):
        get_reference_range(long_param)
    
    # Test with API
    response = client.get(f"/reference/{long_param}")
    assert response.status_code == 404

def test_special_characters():
    """Test with special characters in parameter names."""
    special_chars = "!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~"
    
    for char in special_chars:
        param = f"test{char}param"
        with pytest.raises(ValueError):
            get_reference_range(param)
        
        # Test with API
        response = client.get(f"/reference/{param}")
        assert response.status_code in [404, 422]  # Either not found or validation error

def test_case_sensitivity():
    """Test case sensitivity of parameter names."""
    # These should all work as the lookup is case-insensitive
    variations = [
        "ferritin",
        "Ferritin",
        "FERRITIN",
        "fErRiTiN"
    ]
    
    for var in variations:
        result = get_reference_range(var)
        assert result["parameter"] == var  # Should preserve original case
        assert result["unit"] == "ng/ml"
        
        # Test with API
        response = client.get(f"/reference/{var}")
        assert response.status_code == 200
        assert response.json()["parameter"] == var

def test_none_values():
    """Test behavior with None/Null values."""
    # Test with direct function call - should raise TypeError
    with pytest.raises((TypeError, AttributeError)):
        get_reference_range(None)
    
    # Test with API - None as parameter (should be 404 as it's not a valid URL)
    response = client.get("/reference/None")
    assert response.status_code == 404

def test_extreme_values():
    """Test with extreme values for parameters that accept them."""
    # This test is more relevant for parameters that accept numeric ranges
    # For this API, we're mostly dealing with string lookups, but we can test edge cases
    
    # Test with a very large number as parameter
    with pytest.raises(ValueError):
        get_reference_range("9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999")
    
    # Test with API
    response = client.get("/reference/9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999")
    assert response.status_code == 404

@pytest.mark.parametrize("sex_input,expected_sex,expected_status_code", [
    ("male", Sex.MALE, 200),
    ("female", Sex.FEMALE, 200),
    # Test that only lowercase is accepted by the API
    ("MALE", Sex.MALE, 422),  # Should fail - API expects lowercase
    ("Male", Sex.MALE, 422),  # Should fail - API expects lowercase
    ("FEMALE", Sex.FEMALE, 422),  # Should fail - API expects lowercase
    ("Female", Sex.FEMALE, 422),  # Should fail - API expects lowercase
])
def test_sex_parameter_variations(sex_input, expected_sex, expected_status_code):
    """Test different variations of sex parameter."""
    # Test with direct function call (should work with any case for the enum)
    result = get_reference_range("ferritin", expected_sex)
    assert result["sex_specific"] is True
    
    # Test with API (should only accept lowercase)
    response = client.get(f"/reference/ferritin?sex={sex_input}")
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json()["sex_specific_range"] is not None

def test_concurrent_requests():
    """Test handling of concurrent API requests."""
    import threading
    
    results = {}
    
    def make_request(param, result_key):
        response = client.get(f"/reference/{param}")
        results[result_key] = response.status_code
    
    # Create multiple threads
    threads = []
    for i, param in enumerate(["ferritin", "vitamin d", "tsh"]):
        t = threading.Thread(target=make_request, args=(param, f"result_{i}"))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Verify all requests were successful
    for i in range(3):
        assert results[f"result_{i}"] == 200

def test_error_messages():
    """Test that error messages are clear and helpful."""
    # Test with invalid parameter
    response = client.get("/reference/invalid_parameter_123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Test with invalid sex parameter
    response = client.get("/reference/ferritin?sex=invalid_sex")
    assert response.status_code == 422  # Validation error
    assert "Input should be 'male' or 'female'" in response.text
    
    # Test with BloodTestTool
    tool = BloodTestTool()
    with pytest.raises(HTTPException) as exc_info:
        tool.get_optimal_values("invalid_parameter_123")
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail).lower()
    
    with pytest.raises(HTTPException) as exc_info:
        tool.get_optimal_values("ferritin", "invalid_sex")
    assert exc_info.value.status_code == 400
    assert "Invalid sex" in str(exc_info.value.detail)
