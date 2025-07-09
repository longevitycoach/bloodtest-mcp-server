#!/bin/bash
# Run all MCP integration tests

echo "=== MCP Integration Test Suite ==="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t bloodtest-mcp-server:local -f Dockerfile.optimized . > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi
echo "✅ Docker image built successfully"

# Stop and remove any existing container
docker stop bloodtest-local > /dev/null 2>&1
docker rm bloodtest-local > /dev/null 2>&1

# Start the container
echo "🚀 Starting Docker container..."
docker run -d --name bloodtest-local -p 8001:8000 bloodtest-mcp-server:local > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker container"
    exit 1
fi
echo "✅ Docker container started"

# Wait for server to be ready
echo "⏳ Waiting for server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ Server is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Server failed to start within 30 seconds"
        docker logs bloodtest-local
        exit 1
    fi
    sleep 1
done

# Run the tests
echo
echo "🧪 Running integration tests..."
echo

# Run local health test
python tests/test_local_health.py
HEALTH_RESULT=$?

echo
echo "🧪 Running MCP client tests..."
echo

# Run MCP integration tests
python tests/test_mcp_client.py
MCP_RESULT=$?

# Clean up
echo
echo "🧹 Cleaning up..."
docker stop bloodtest-local > /dev/null 2>&1
docker rm bloodtest-local > /dev/null 2>&1
echo "✅ Cleanup complete"

# Summary
echo
echo "=== Test Summary ==="
if [ $HEALTH_RESULT -eq 0 ] && [ $MCP_RESULT -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi