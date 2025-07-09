# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive health coaching system that combines blood test analysis with evidence-based nutritional therapy recommendations. It uses:
- **FastMCP** for MCP protocol support
- **FAISS** for RAG (Retrieval-Augmented Generation) with medical knowledge
- **FastAPI** for REST API endpoints
- **Docker** for containerization

## Common Development Commands

### Setup and Installation
```bash
# Create virtual environment and install dependencies
make setup

# Or manually:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Application
```bash
# Run the MCP server locally (with health endpoint)
python start_server.py

# The server will:
# - Start on http://localhost:8000 (or PORT env variable)
# - Provide health endpoint at /health
# - Provide MCP SSE endpoint at /sse
# - Load configuration from resources/structure.yaml

# Run just the FastAPI server (blood test API only)
python main.py  # or: python -m uvicorn bloodtest_tools.api:app --reload

# Using Docker
docker-compose up --build
```

### Testing
```bash
# Run all tests with coverage
make test
# or
pytest tests/ -v --cov=bloodtest_tools --cov-report=term-missing

# Run specific test file
pytest tests/test_api_endpoints.py -v

# Run a single test
pytest tests/test_api_endpoints.py::test_root_endpoint -v
```

### Code Quality
```bash
# Run linting
make lint

# Format code
make format
```

### RAG Initialization
```bash
# Initialize the FAISS index from PDFs
INDEX_NAME="supplement-therapy" PDF_DIRECTORY="resources/books" python scripts/init_rag.py
```

## High-Level Architecture

### Core Components

1. **MCP Server (`server.py`)**: 
   - Main entry point for MCP protocol support
   - Dynamically generates tools from workflows defined in `resources/structure.yaml`
   - Integrates RAG system for knowledge retrieval
   - Provides SSE (Server-Sent Events) transport at `/sse`

2. **Integrated Server (`integrated_server.py`)**:
   - Combines MCP tools with REST API endpoints
   - Provides both blood test reference API and MCP protocol support
   - Used for deployment scenarios requiring both interfaces

3. **Blood Test Tools (`bloodtest_tools/`)**:
   - `reference_values.py`: Contains medical reference ranges for blood tests
   - `api.py`: FastAPI endpoints for blood test parameter queries
   - `mcp_tool.py`: MCP tool wrapper for blood test functionality

4. **RAG System (`utils/rag_system.py`)**:
   - Uses FAISS for vector similarity search
   - Indexes medical PDFs for evidence-based recommendations
   - Configured via `structure.yaml` with index name matching requirement

5. **Workflow Engine**:
   - Defined in `resources/structure.yaml`
   - Supports complex multi-step health coaching workflows
   - Each workflow becomes an MCP tool automatically

### Key Configuration Files

- **`resources/structure.yaml`**: Defines workflows, tools, and RAG configuration. Critical that `rag.config.index_name` matches the FAISS index name.
- **`docker-compose.yml`**: Docker configuration with environment variables
- **`requirements.txt`**: Python dependencies

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /parameters` - List blood test parameters
- `GET /reference/{parameter}` - Get reference ranges
- `GET /sse` - MCP Server-Sent Events endpoint

### MCP Tools

Generated dynamically from workflows plus:
- `get_book_info` - Returns metadata about loaded knowledge
- `list_workflows` - Lists available health coaching workflows
- `supplement_therapy` - Main health coaching workflow
- `search_book_knowledge` - RAG search through medical texts
- `sequential_thinking` - Multi-step reasoning tool

## Important Patterns

1. **Configuration Loading**: The code searches multiple paths for config files to support both local development and Docker deployment
2. **Error Handling**: Comprehensive try-catch blocks with logging
3. **Health Checks**: Available at `/health` for monitoring
4. **CORS**: Enabled for HTTP transports to support web clients
5. **Logging**: Configurable via ENV variable (DEBUG in DEV, INFO otherwise)

## Deployment Considerations

- The application is configured for Railway deployment
- Uses `0.0.0.0` as host to allow external connections in containers
- Port is configurable via PORT environment variable
- FAISS index must be initialized before deployment (included in Docker image)