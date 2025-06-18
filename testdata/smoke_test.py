#!/usr/bin/env python3
"""
Quick Smoke Test for Bloodtest MCP Server
Performs rapid validation of core functionality
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

async def smoke_test():
    """Run quick smoke test of core functionality"""
    print("🩸 Bloodtest MCP Server - Quick Smoke Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    results = {"passed": 0, "failed": 0, "tests": []}
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        
        # Test 1: Health Check
        try:
            async with session.get(f"{base_url}/health") as resp:
                data = await resp.json()
                if resp.status == 200 and data.get("status") == "healthy":
                    print("✅ Health check - PASSED")
                    results["passed"] += 1
                    results["tests"].append({"test": "health_check", "status": "PASSED", "rag_enabled": data.get("rag_enabled")})
                else:
                    print("❌ Health check - FAILED")
                    results["failed"] += 1
                    results["tests"].append({"test": "health_check", "status": "FAILED"})
        except Exception as e:
            print(f"❌ Health check - FAILED ({str(e)})")
            results["failed"] += 1
            results["tests"].append({"test": "health_check", "status": "FAILED", "error": str(e)})
        
        # Test 2: API Root
        try:
            async with session.get(f"{base_url}/") as resp:
                data = await resp.json()
                if resp.status == 200 and "Blood Test Reference Values API" in data.get("name", ""):
                    print("✅ API root endpoint - PASSED")
                    results["passed"] += 1
                    results["tests"].append({"test": "api_root", "status": "PASSED"})
                else:
                    print("❌ API root endpoint - FAILED")
                    results["failed"] += 1
                    results["tests"].append({"test": "api_root", "status": "FAILED"})
        except Exception as e:
            print(f"❌ API root endpoint - FAILED ({str(e)})")
            results["failed"] += 1
            results["tests"].append({"test": "api_root", "status": "FAILED", "error": str(e)})
        
        # Test 3: Parameters List
        try:
            async with session.get(f"{base_url}/parameters") as resp:
                data = await resp.json()
                params = data.get("parameters", [])
                if resp.status == 200 and len(params) >= 8:
                    print("✅ Parameters endpoint - PASSED")
                    results["passed"] += 1
                    results["tests"].append({"test": "parameters_list", "status": "PASSED", "param_count": len(params)})
                else:
                    print("❌ Parameters endpoint - FAILED")
                    results["failed"] += 1
                    results["tests"].append({"test": "parameters_list", "status": "FAILED"})
        except Exception as e:
            print(f"❌ Parameters endpoint - FAILED ({str(e)})")
            results["failed"] += 1
            results["tests"].append({"test": "parameters_list", "status": "FAILED", "error": str(e)})
        
        # Test 4: Ferritin Reference
        try:
            async with session.get(f"{base_url}/reference/ferritin") as resp:
                data = await resp.json()
                if resp.status == 200 and data.get("parameter") == "ferritin" and data.get("unit") == "ng/ml":
                    print("✅ Ferritin reference - PASSED")
                    results["passed"] += 1
                    results["tests"].append({"test": "ferritin_reference", "status": "PASSED"})
                else:
                    print("❌ Ferritin reference - FAILED")
                    results["failed"] += 1
                    results["tests"].append({"test": "ferritin_reference", "status": "FAILED"})
        except Exception as e:
            print(f"❌ Ferritin reference - FAILED ({str(e)})")
            results["failed"] += 1
            results["tests"].append({"test": "ferritin_reference", "status": "FAILED", "error": str(e)})
        
        # Test 5: Sex-specific Reference
        try:
            async with session.get(f"{base_url}/reference/ferritin?sex=female") as resp:
                data = await resp.json()
                if resp.status == 200 and data.get("sex_specific") and "sex_specific_range" in data:
                    print("✅ Sex-specific reference - PASSED")
                    results["passed"] += 1
                    results["tests"].append({"test": "sex_specific_reference", "status": "PASSED"})
                else:
                    print("❌ Sex-specific reference - FAILED")
                    results["failed"] += 1
                    results["tests"].append({"test": "sex_specific_reference", "status": "FAILED"})
        except Exception as e:
            print(f"❌ Sex-specific reference - FAILED ({str(e)})")
            results["failed"] += 1
            results["tests"].append({"test": "sex_specific_reference", "status": "FAILED", "error": str(e)})
        
        # Test 6: Error Handling
        try:
            async with session.get(f"{base_url}/reference/invalid_param") as resp:
                if resp.status == 404:
                    print("✅ Error handling - PASSED")
                    results["passed"] += 1
                    results["tests"].append({"test": "error_handling", "status": "PASSED"})
                else:
                    print("❌ Error handling - FAILED")
                    results["failed"] += 1
                    results["tests"].append({"test": "error_handling", "status": "FAILED"})
        except Exception as e:
            print(f"❌ Error handling - FAILED ({str(e)})")
            results["failed"] += 1
            results["tests"].append({"test": "error_handling", "status": "FAILED", "error": str(e)})
        
        # Test 7: MCP SSE Endpoint
        try:
            async with session.get(f"{base_url}/sse") as resp:
                if resp.status == 200:
                    print("✅ MCP SSE endpoint - PASSED")
                    results["passed"] += 1
                    results["tests"].append({"test": "mcp_sse_endpoint", "status": "PASSED"})
                else:
                    print("❌ MCP SSE endpoint - FAILED")
                    results["failed"] += 1
                    results["tests"].append({"test": "mcp_sse_endpoint", "status": "FAILED"})
        except Exception as e:
            print(f"❌ MCP SSE endpoint - FAILED ({str(e)})")
            results["failed"] += 1
            results["tests"].append({"test": "mcp_sse_endpoint", "status": "FAILED", "error": str(e)})
    
    # Summary
    total_tests = results["passed"] + results["failed"]
    success_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 50)
    print("📊 Smoke Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if results["failed"] == 0:
        print("\n🎉 All smoke tests passed! System is ready for comprehensive testing.")
        return True
    else:
        print(f"\n⚠️  {results['failed']} smoke tests failed. Check server configuration and try again.")
        return False

def check_test_data_files():
    """Check if test data files exist"""
    testdata_dir = Path(".")
    required_files = [
        "comprehensive_api_tests.json",
        "comprehensive_mcp_tool_tests.json", 
        "realistic_blood_analysis_scenarios.json",
        "test_runner.py",
        "validate_test_data.py"
    ]
    
    print("\n📁 Test Data Files Check:")
    missing_files = []
    for file_name in required_files:
        file_path = testdata_dir / file_name
        if file_path.exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} - MISSING")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} test data files. Generate them before running comprehensive tests.")
        return False
    else:
        print("\n✅ All test data files present.")
        return True

async def main():
    """Main function"""
    print("Starting Bloodtest MCP Server smoke test...\n")
    
    # Check test data files
    files_ok = check_test_data_files()
    
    # Run smoke tests
    smoke_ok = await smoke_test()
    
    # Final recommendations
    print("\n💡 Next Steps:")
    if smoke_ok and files_ok:
        print("   • Run comprehensive tests: python test_runner.py")
        print("   • Validate test data: python validate_test_data.py")
        print("   • Check performance: python test_runner.py --suite performance")
    elif smoke_ok:
        print("   • Generate missing test data files")
        print("   • Ensure all test configurations are complete")
    else:
        print("   • Check server configuration and restart if needed")
        print("   • Verify all dependencies are installed")
        print("   • Check logs for specific error details")
    
    return smoke_ok and files_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)