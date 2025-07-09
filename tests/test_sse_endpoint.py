"""
Integration tests for the SSE endpoint of the Blood Test MCP Server.

These tests verify the Server-Sent Events (SSE) functionality of the MCP server.

To run tests against the production endpoint, use:
    TEST_BASE_URL=https://supplement-therapy.up.railway.app pytest tests/test_sse_endpoint.py -m production -v
"""

# Register custom markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "production: mark test as requiring production endpoint"
    )
import os
import json
import pytest
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any
from httpx import AsyncClient
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def base_url():
    """Get the base URL from environment variable or use default."""
    return os.getenv("TEST_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def sse_endpoint(base_url):
    return f"{base_url}/sse"

# Test data
TEST_TOOL_NAME = "search_book_knowledge"
TEST_QUERY = "What are the benefits of Vitamin D?"

@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.production
@pytest.mark.asyncio
async def test_sse_connection(sse_endpoint):
    """Test that we can establish a connection to the SSE endpoint."""
    async with AsyncClient(timeout=30.0) as client:
        logger.info(f"Testing connection to SSE endpoint: {sse_endpoint}")
        
        # Try to connect to SSE endpoint
        try:
            async with client.stream("GET", sse_endpoint, timeout=30.0) as response:
                assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
                assert "text/event-stream" in response.headers.get("content-type", ""), \
                    f"Expected content-type to contain 'text/event-stream', got {response.headers.get('content-type')}"
                logger.info("Successfully connected to SSE endpoint")
        except Exception as e:
            pytest.fail(f"Failed to connect to SSE endpoint: {e}")

@pytest.mark.production
@pytest.mark.asyncio
async def test_sse_event_stream(sse_endpoint):
    """Test that the SSE endpoint sends events in the expected format."""
    async with AsyncClient(timeout=30.0) as client:
        logger.info(f"Testing SSE event stream from: {sse_endpoint}")
        
        # Connect to SSE endpoint
        async with client.stream("GET", sse_endpoint, timeout=30.0) as response:
            assert response.status_code == 200
            
            # Read the first few events
            event_count = 0
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                    
                # Log the event for debugging
                logger.debug(f"Received SSE event: {line}")
                
                # Basic validation of SSE event format
                if line.startswith("event:") or line.startswith("data:"):
                    event_count += 1
                
                # Stop after receiving a few events
                if event_count >= 3:
                    break
            
            assert event_count > 0, "No SSE events were received"

@pytest.mark.production
@pytest.mark.asyncio
async def test_mcp_tool_invocation(sse_endpoint):
    """Test invoking an MCP tool through the SSE endpoint."""
    # This is a simplified test that would need to be adapted to your actual MCP protocol
    async with AsyncClient(timeout=30.0) as client:
        logger.info(f"Testing MCP tool invocation through SSE: {sse_endpoint}")
        
        # Prepare a test message (this would need to match your MCP protocol)
        test_message = {
            "jsonrpc": "2.0",
            "method": "mcp.tool.invoke",
            "params": {
                "tool": TEST_TOOL_NAME,
                "args": {"query": TEST_QUERY}
            },
            "id": 1
        }
        
        # Connect to SSE endpoint
        async with client.stream(
                "GET",  
                f"{sse_endpoint}?tool={TEST_TOOL_NAME}&query={TEST_QUERY}",
                headers={"Accept": "text/event-stream"},
                timeout=30.0,
                verify=False  
        ) as response:
            assert response.status_code == 200
            
            # Process the response stream
            response_received = False
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                    
                logger.debug(f"Received SSE response: {line}")
                
                # Look for a data line with our response
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if "result" in data:
                            response_received = True
                            logger.info(f"Received tool response: {data}")
                            break
                    except json.JSONDecodeError:
                        continue
            
            assert response_received, "No valid response received from the tool"

@pytest.mark.production
@pytest.mark.asyncio
async def test_health_endpoint(base_url):
    """Test the health check endpoint."""
    async with AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{base_url}/health", timeout=30.0)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        logger.info(f"Health check response: {data}")

# Example of a more complex test with mocked responses
@pytest.mark.asyncio
async def test_sse_with_mocked_responses(httpx_mock, sse_endpoint):
    """Test SSE with mocked responses for faster testing."""
    # Mock the SSE endpoint
    mock_response = [
        "event: message\ndata: {\"status\": \"connected\"}\n\n",
        "event: tool_response\ndata: {\"result\": \"Mocked response\"}\n\n"
    ]
    
    # Configure the mock
    httpx_mock.add_response(
        method="GET",
        url=sse_endpoint,
        content="".join(mock_response).encode(),
        headers={"Content-Type": "text/event-stream"}
    )
    
    # Make the request to the mocked endpoint
    async with AsyncClient() as client:
        async with client.stream("GET", SSE_ENDPOINT) as response:
            assert response.status_code == 200
            
            events = []
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    events.append(line[5:].strip())
            
            assert len(events) > 0
            logger.info(f"Mocked SSE events: {events}")
