#!/usr/bin/env python3
"""
Local Health Check Test
Simple script to verify local deployment health
"""
import requests
import json
import sys
import time

def test_local_health(port=8001):
    """Test local Docker deployment health"""
    base_url = f"http://localhost:{port}"
    
    print(f"Testing local deployment at {base_url}")
    print("-" * 50)
    
    # Test 1: Health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {data.get('status')}")
            print(f"   ✓ Book: {data.get('book')}")
            print(f"   ✓ Version: {data.get('version')}")
            print(f"   ✓ RAG Enabled: {data.get('rag_enabled')}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: SSE endpoint availability
    print("\n2. Testing /sse endpoint...")
    try:
        response = requests.get(f"{base_url}/sse", stream=True, timeout=5)
        if response.status_code == 200:
            print("   ✓ SSE endpoint is accessible")
            response.close()
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Invalid endpoint (should return 404)
    print("\n3. Testing invalid endpoint handling...")
    try:
        response = requests.get(f"{base_url}/invalid", timeout=5)
        if response.status_code == 404:
            print("   ✓ Correctly returns 404 for invalid endpoint")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Response time
    print("\n4. Testing response time...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response_time = (time.time() - start_time) * 1000  # ms
        if response_time < 1000:  # Should respond within 1 second
            print(f"   ✓ Response time: {response_time:.2f}ms")
        else:
            print(f"   ⚠ Slow response time: {response_time:.2f}ms")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "-" * 50)
    print("✅ All health checks passed!")
    return True


def main():
    """Main function"""
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8001
    
    print("=== Local Health Check Test ===\n")
    
    # Check if Docker container is running
    try:
        success = test_local_health(port)
        if success:
            print("\n✅ Local deployment is healthy!")
            return 0
        else:
            print("\n❌ Local deployment has issues!")
            return 1
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to server at http://localhost:{port}")
        print("\nPlease ensure the Docker container is running:")
        print("  docker run -d --name bloodtest-local -p 8001:8000 bloodtest-mcp-server:local")
        return 1


if __name__ == "__main__":
    sys.exit(main())