#!/usr/bin/env python3
"""
Test script for the Blood Test Reference Values API.
"""
import sys
import requests
import json

def test_root_endpoint(base_url):
    """Test the root endpoint."""
    print("\n1. Testing GET /")
    try:
        response = requests.get(f"{base_url}/")
        response.raise_for_status()
        data = response.json()
        print("Success! Root endpoint response:")
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_parameters(base_url):
    """Test the list parameters endpoint."""
    print("\n2. Testing GET /parameters")
    try:
        response = requests.get(f"{base_url}/parameters")
        response.raise_for_status()
        data = response.json()
        param_count = len(data.get('parameters', []))
        print(f"Success! Found {param_count} parameters")
        print(json.dumps(data, indent=2))
        return param_count > 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_reference_range(base_url, parameter, sex=None):
    """Test getting a reference range for a parameter."""
    test_name = f"{parameter} (sex: {sex if sex else 'not specified'})"
    print(f"\n3. Testing GET /reference/{test_name}")
    
    url = f"{base_url}/reference/{parameter}"
    if sex:
        url += f"?sex={sex}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Success! Reference range for {test_name}:")
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_parameter(base_url):
    """Test error handling for an invalid parameter."""
    invalid_param = "invalid_parameter_123"
    print(f"\n4. Testing error handling with invalid parameter: {invalid_param}")
    
    try:
        response = requests.get(f"{base_url}/reference/{invalid_param}")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 404
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_all_tests(base_url):
    """Run all test cases."""
    print(f"Testing Blood Test Reference Values API at {base_url}")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(('Root endpoint', test_root_endpoint(base_url)))
    results.append(('List parameters', test_list_parameters(base_url)))
    results.append(('Get reference range (no sex)', 
                   test_reference_range(base_url, "ferritin")))
    results.append(('Get reference range (with sex)', 
                   test_reference_range(base_url, "ferritin", "female")))
    results.append(('Invalid parameter handling', 
                   test_invalid_parameter(base_url)))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY:")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name:40} {status}")
        all_passed = all_passed and passed
    
    print("\n" + "=" * 70)
    if all_passed:
        print("All tests passed successfully!")
    else:
        print("Some tests failed. Please check the output above for details.")
    
    return all_passed

def main():
    # Default to localhost:8000 if no arguments provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    if not run_all_tests(base_url):
        sys.exit(1)

if __name__ == "__main__":
    main()
