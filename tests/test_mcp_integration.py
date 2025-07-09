"""
MCP Integration Tests using SSE Protocol
Tests both positive and negative scenarios based on the medical knowledge books
"""
import asyncio
import json
import aiohttp
import pytest
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
MCP_SSE_URL = "http://localhost:8001/sse"
TIMEOUT = 30

class MCPTestClient:
    """Test client for MCP SSE communication"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = None
        
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send MCP request and get response"""
        request_id = f"test-{method}-{asyncio.get_event_loop().time()}"
        
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        async with aiohttp.ClientSession() as session:
            # Initialize SSE connection
            async with session.get(self.base_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to connect to SSE endpoint: {response.status}")
                
                # Get session ID from SSE stream
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        data = json.loads(line_str[6:])
                        if 'session_id' in data:
                            self.session_id = data['session_id']
                            break
            
            # Send the actual request
            if not self.session_id:
                raise Exception("Failed to get session ID")
                
            url = f"{self.base_url.replace('/sse', '')}/messages/?session_id={self.session_id}"
            async with session.post(url, json=request_data) as response:
                if response.status != 202:
                    raise Exception(f"Request failed: {response.status}")
            
            # Get response from SSE stream
            async with session.get(self.base_url) as response:
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        data = json.loads(line_str[6:])
                        if data.get('id') == request_id:
                            return data

@pytest.mark.asyncio
class TestMCPIntegration:
    """Integration tests for MCP server"""
    
    @pytest.fixture
    async def client(self):
        """Create MCP test client"""
        return MCPTestClient(MCP_SSE_URL)
    
    # ========== POSITIVE TEST CASES ==========
    
    async def test_01_get_book_info(self, client):
        """Test getting book information"""
        response = await client.send_request("tools/call", {
            "name": "get_book_info",
            "arguments": {}
        })
        
        assert response is not None
        result = response.get('result', {})
        assert result.get('title') == "Der Blutwerte Coach, Naehrstoff-Therapie"
        assert result.get('rag_enabled') is True
        assert 'available_workflows' in result
        logger.info("✓ Successfully retrieved book information")
    
    async def test_02_list_workflows(self, client):
        """Test listing available workflows"""
        response = await client.send_request("tools/call", {
            "name": "list_workflows",
            "arguments": {}
        })
        
        assert response is not None
        result = response.get('result', [])
        assert isinstance(result, list)
        assert len(result) > 0
        assert any('Supplement Therapy' in w.get('name', '') for w in result)
        logger.info("✓ Successfully listed workflows")
    
    async def test_03_search_ferritin_knowledge(self, client):
        """Test searching for ferritin information in knowledge base"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "ferritin optimal range women"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        assert 'results' in result
        assert len(result['results']) > 0
        logger.info("✓ Successfully searched ferritin knowledge")
    
    async def test_04_search_vitamin_d_deficiency(self, client):
        """Test searching for vitamin D deficiency symptoms"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "vitamin D mangel symptome"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        assert 'results' in result
        assert any('vitamin' in str(r).lower() for r in result['results'])
        logger.info("✓ Successfully searched vitamin D deficiency")
    
    async def test_05_search_magnesium_supplementation(self, client):
        """Test searching for magnesium supplementation guidance"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "magnesium supplementierung dosierung"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        assert 'results' in result
        logger.info("✓ Successfully searched magnesium supplementation")
    
    async def test_06_search_thyroid_tsh_interpretation(self, client):
        """Test searching for TSH interpretation"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "TSH wert interpretation schilddrüse"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        assert 'results' in result
        logger.info("✓ Successfully searched TSH interpretation")
    
    async def test_07_supplement_therapy_workflow(self, client):
        """Test supplement therapy workflow execution"""
        response = await client.send_request("tools/call", {
            "name": "supplement_therapy",
            "arguments": {}
        })
        
        assert response is not None
        result = response.get('result', '')
        assert isinstance(result, str)
        assert len(result) > 100  # Should return detailed prompt
        logger.info("✓ Successfully executed supplement therapy workflow")
    
    async def test_08_search_b12_holotranscobalamin(self, client):
        """Test searching for B12 Holotranscobalamin information"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "holotranscobalamin B12 optimal"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        assert 'results' in result
        logger.info("✓ Successfully searched B12 information")
    
    async def test_09_search_selenium_immune_system(self, client):
        """Test searching for selenium and immune system"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "selen immunsystem dosierung"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        assert 'results' in result
        logger.info("✓ Successfully searched selenium information")
    
    async def test_10_search_zinc_copper_ratio(self, client):
        """Test searching for zinc-copper ratio information"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "zink kupfer verhältnis supplementierung"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        assert 'results' in result
        logger.info("✓ Successfully searched zinc-copper ratio")
    
    # ========== NEGATIVE TEST CASES ==========
    
    async def test_11_invalid_tool_name(self, client):
        """Test calling non-existent tool"""
        with pytest.raises(Exception) as exc_info:
            await client.send_request("tools/call", {
                "name": "non_existent_tool",
                "arguments": {}
            })
        assert "not found" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
        logger.info("✓ Correctly rejected invalid tool name")
    
    async def test_12_missing_tool_arguments(self, client):
        """Test calling tool without required arguments"""
        with pytest.raises(Exception) as exc_info:
            await client.send_request("tools/call", {
                "name": "search_book_knowledge"
                # Missing 'arguments' field
            })
        logger.info("✓ Correctly rejected missing arguments")
    
    async def test_13_empty_search_query(self, client):
        """Test searching with empty query"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": ""
            }
        })
        
        # Should either return empty results or raise an error
        if 'error' in response:
            assert True
        else:
            result = response.get('result', {})
            assert result.get('results', []) == []
        logger.info("✓ Correctly handled empty search query")
    
    async def test_14_invalid_method_name(self, client):
        """Test calling invalid MCP method"""
        with pytest.raises(Exception) as exc_info:
            await client.send_request("invalid/method", {})
        logger.info("✓ Correctly rejected invalid method")
    
    async def test_15_malformed_json_request(self, client):
        """Test sending malformed request"""
        # This would be handled at protocol level
        with pytest.raises(Exception):
            # Simulate malformed request by corrupting session
            client.session_id = "invalid-session"
            await client.send_request("tools/call", {
                "name": "get_book_info",
                "arguments": {}
            })
        logger.info("✓ Correctly rejected malformed request")
    
    async def test_16_search_nonsense_query(self, client):
        """Test searching with nonsense query"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "xyzabc123nonsense"
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        # Should return results but they might not be relevant
        assert 'results' in result
        logger.info("✓ Handled nonsense query gracefully")
    
    async def test_17_exceed_search_limit(self, client):
        """Test searching with very high k value"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "vitamin",
                "k": 1000  # Unreasonably high
            }
        })
        
        assert response is not None
        result = response.get('result', {})
        # Should cap at reasonable limit
        assert len(result.get('results', [])) <= 20
        logger.info("✓ Correctly limited search results")
    
    async def test_18_special_characters_query(self, client):
        """Test searching with special characters"""
        response = await client.send_request("tools/call", {
            "name": "search_book_knowledge",
            "arguments": {
                "query": "test!@#$%^&*()"
            }
        })
        
        assert response is not None
        # Should handle gracefully without crashing
        logger.info("✓ Handled special characters gracefully")
    
    async def test_19_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        tasks = []
        for i in range(5):
            task = client.send_request("tools/call", {
                "name": "get_book_info",
                "arguments": {}
            })
            tasks.append(task)
        
        # Should handle all requests without errors
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if not isinstance(r, Exception))
        assert successful >= 3  # At least 3 should succeed
        logger.info("✓ Handled concurrent requests")
    
    async def test_20_invalid_workflow_execution(self, client):
        """Test executing workflow with invalid parameters"""
        with pytest.raises(Exception):
            await client.send_request("tools/call", {
                "name": "supplement_therapy",
                "arguments": {
                    "invalid_param": "value"
                }
            })
        logger.info("✓ Correctly rejected invalid workflow parameters")


# Local health check test
def test_local_health_check():
    """Test local Docker deployment health check"""
    import requests
    
    response = requests.get("http://localhost:8001/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['book'] == "Der Blutwerte Coach, Naehrstoff-Therapie"
    assert data['rag_enabled'] is True
    
    logger.info("✓ Local health check passed")


if __name__ == "__main__":
    # Run the health check first
    print("\n=== Running Local Health Check ===")
    test_local_health_check()
    
    # Run all integration tests
    print("\n=== Running MCP Integration Tests ===")
    pytest.main([__file__, "-v", "-s"])