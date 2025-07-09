#!/usr/bin/env python3
"""
Validate Railway Deployment
Comprehensive check of production deployment
"""
import requests
import json
import time
import sys
from datetime import datetime

# Production endpoint
BASE_URL = "https://supplement-therapy.up.railway.app"

def validate_deployment():
    """Run comprehensive deployment validation"""
    print("=== Railway Deployment Validation ===")
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
    
    # Test 2: SSE endpoint
    print("\n2. Testing SSE Endpoint...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/sse", stream=True, timeout=10)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            print(f"   ✅ SSE endpoint accessible")
            print(f"   ✅ Content-Type: {response.headers.get('content-type')}")
            print(f"   ✅ Response Time: {elapsed:.2f}ms")
            response.close()
            results.append(True)
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Test 3: Parameters endpoint
    print("\n3. Testing Parameters Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/parameters", timeout=10)
        if response.status_code == 200:
            data = response.json()
            params = data.get('parameters', [])
            print(f"   ✅ Available parameters: {len(params)}")
            print(f"   ✅ Sample parameters: {params[:3]}...")
            results.append(True)
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Test 4: Reference endpoint
    print("\n4. Testing Reference Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/reference/ferritin?sex=female", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Ferritin reference retrieved")
            print(f"   ✅ Unit: {data.get('unit')}")
            print(f"   ✅ Optimal range: {data.get('optimal_range')}")
            results.append(True)
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Test 5: Performance check
    print("\n5. Testing Performance...")
    response_times = []
    try:
        for i in range(5):
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            elapsed = (time.time() - start) * 1000
            response_times.append(elapsed)
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"   ✅ Average response time: {avg_time:.2f}ms")
        print(f"   ✅ Min response time: {min_time:.2f}ms")
        print(f"   ✅ Max response time: {max_time:.2f}ms")
        
        if avg_time < 1000:  # Less than 1 second
            print(f"   ✅ Performance: GOOD")
            results.append(True)
        else:
            print(f"   ⚠️  Performance: SLOW")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Deployment Validation Summary:")
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.0f}%")
    
    if passed == total:
        print("\n✅ Railway deployment is fully operational!")
        return 0
    else:
        print(f"\n⚠️  Railway deployment has {total - passed} issues!")
        return 1

if __name__ == "__main__":
    sys.exit(validate_deployment())