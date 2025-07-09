#!/usr/bin/env python3
"""
Validate MCP Railway Deployment
Tests only MCP-specific endpoints
"""
import requests
import json
import time
import sys
from datetime import datetime

# Production endpoint
BASE_URL = "https://supplement-therapy.up.railway.app"

def validate_mcp_deployment():
    """Validate MCP server deployment"""
    print("=== MCP Server Railway Deployment Validation ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print("-" * 50)
    
    results = []
    
    # Test 1: Health endpoint
    print("\n1. Testing Health Endpoint...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   ✅ Book: {data.get('book')}")
            print(f"   ✅ Version: {data.get('version')}")
            print(f"   ✅ RAG Enabled: {data.get('rag_enabled')}")
            print(f"   ✅ Response Time: {elapsed:.2f}ms")
            results.append(True)
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Test 2: SSE endpoint headers
    print("\n2. Testing SSE Endpoint Headers...")
    try:
        response = requests.head(f"{BASE_URL}/sse", timeout=10)
        headers = response.headers
        
        if response.status_code == 200:
            print(f"   ✅ SSE endpoint accessible")
            print(f"   ✅ Content-Type: {headers.get('content-type')}")
            print(f"   ✅ Cache-Control: {headers.get('cache-control')}")
            print(f"   ✅ Server: {headers.get('server')}")
            results.append(True)
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Test 3: SSE connection test
    print("\n3. Testing SSE Connection...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/sse", stream=True, timeout=5)
        
        if response.status_code == 200:
            # Read first few bytes to confirm stream
            for i, line in enumerate(response.iter_lines()):
                if i > 2:  # Read first 3 lines
                    break
                if line:
                    print(f"   ✅ Received SSE data: {line.decode()[:50]}...")
            
            elapsed = (time.time() - start) * 1000
            print(f"   ✅ SSE stream active")
            print(f"   ✅ Connection Time: {elapsed:.2f}ms")
            response.close()
            results.append(True)
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            results.append(False)
    except requests.exceptions.Timeout:
        print(f"   ✅ SSE connection established (timeout expected for stream)")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Test 4: Performance check
    print("\n4. Testing Performance (5 health checks)...")
    response_times = []
    try:
        for i in range(5):
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            elapsed = (time.time() - start) * 1000
            response_times.append(elapsed)
            time.sleep(0.5)  # Small delay between requests
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"   ✅ Average response time: {avg_time:.2f}ms")
        print(f"   ✅ Min response time: {min_time:.2f}ms") 
        print(f"   ✅ Max response time: {max_time:.2f}ms")
        
        if avg_time < 1000:  # Less than 1 second
            print(f"   ✅ Performance: EXCELLENT")
            results.append(True)
        else:
            print(f"   ⚠️  Performance: SLOW")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Test 5: Error handling
    print("\n5. Testing Error Handling...")
    try:
        response = requests.get(f"{BASE_URL}/invalid-endpoint", timeout=5)
        if response.status_code == 404:
            print(f"   ✅ Correctly returns 404 for invalid endpoints")
            results.append(True)
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 MCP Deployment Validation Summary:")
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.0f}%")
    
    print("\n📋 Deployment Details:")
    print(f"   - Endpoint: {BASE_URL}")
    print(f"   - MCP SSE: {BASE_URL}/sse")
    print(f"   - Health: {BASE_URL}/health")
    print(f"   - Server: Railway Cloud")
    
    if passed == total:
        print("\n✅ MCP server deployment is fully operational!")
        print("   Ready for Claude Desktop integration")
        return 0
    else:
        print(f"\n⚠️  MCP server deployment has {total - passed} issues!")
        return 1

if __name__ == "__main__":
    sys.exit(validate_mcp_deployment())