# Bloodtest MCP Server

A comprehensive health coaching system that combines blood test analysis with evidence-based nutritional therapy recommendations, powered by Retrieval-Augmented Generation (RAG) technology.

## Table of Contents

- [User Manual](#user-manual)
  - [Key Features](#key-features)
  - [Getting Started](#getting-started)
  - [MCP Configuration](#mcp-configuration)
  - [Using the Health Coach](#using-the-health-coach)
- [Developer Manual](#developer-manual)
  - [API Documentation](#api-documentation)
  - [Technical Stack](#technical-stack)
  - [Installation](#installation)
  - [Development Setup](#development-setup)
  - [Testing](#testing)
  - [Deployment](#deployment)

## User Manual

### Key Features

- **Blood Test Analysis**: Get optimal ranges for key health markers
- **Personalized Recommendations**: Evidence-based supplement and lifestyle advice
- **Medical Knowledge Base**: Powered by German medical literature
- **Multi-format Support**: Upload blood test results in various formats


### Getting Started

1. **Access the System**
   - Web Interface: [https://supplement-therapy.up.railway.app](https://supplement-therapy.up.railway.app)  
   - API Base URL: `https://supplement-therapy.up.railway.app/sse`

2. **Authentication**
   - Obtain API keys from the system administrator
   - Include the API key in the `Authorization` header of your requests

### MCP Configuration

#### Claude Desktop Integration

To use this MCP server with Claude Desktop:

1. **Open Claude Desktop Configuration**
   - Click on **Claude** menu (macOS) or **File** menu (Windows)
   - Select **Settings** → **Developer** → **Edit Config**

2. **Add Server Configuration**
   Add the following to your `claude_desktop_config.json`:

   ```json
   {
     "mcpServers": {
       "bloodtest-health-coach": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-sse",
           "https://supplement-therapy.up.railway.app/sse"
         ],
         "env": {}
       }
     }
   }
   ```

3. **Save and Restart Claude Desktop**
   - Save the configuration file
   - Completely quit and restart Claude Desktop
   - The health coach tools should now appear in Claude

**Configuration File Locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

#### Available Tools

1. **`get_book_info`**

   - Returns metadata about the loaded medical books and available workflows
   - Example usage: `mcp-cli get_book_info`

2. **`list_workflows`**

   - Lists all available health coaching workflows
   - Example: `mcp-cli list_workflows`

3. **`supplement_therapy`**

   - Main health coaching workflow for personalized supplement recommendations
   - Requires patient assessment data

4. **`search_book_knowledge`**
   - Search through indexed medical knowledge base
   - Example: `mcp-cli search_book_knowledge "optimal ferritin levels"`

#### Configuration File

Create a `config.yaml` file with the following structure:

```yaml
mcp:
  host: localhost
  port: 8000
  api_key: your_api_key_here
  
vector_store:
  index_name: supplement-therapy
  pdf_directory: resources/books
  
server:
  debug: false
  log_level: info
```

### Using the Health Coach

1. **Upload Blood Test**
   - Supported formats: PDF, JPG, PNG
   - German lab reports are automatically parsed

2. **Complete Health Assessment**
   - Provide information about your symptoms and lifestyle
   - Set your health goals

3. **Receive Recommendations**
   - Personalized supplement plan
   - Dietary suggestions
   - Lifestyle modifications

## Developer Manual

### API Documentation

### Base URLs

- **Production**: `https://supplement-therapy.up.railway.app`
- **Local Development**: `http://localhost:8000`
- **SSE Endpoint**: `/sse` (for Server-Sent Events when MCP is enabled)

### Authentication

Most endpoints are publicly accessible, but for production use, you should implement authentication. The API supports Bearer token authentication:

```http
Authorization: Bearer your_api_key_here
```

### Core Endpoints

#### 1. API Information

- **Endpoint**: `GET /`
- **Description**: Get information about the API and available endpoints
- **Response**:
  ```json
  {
    "name": "Blood Test Reference Values API",
    "version": "1.0.0",
    "description": "API for retrieving optimal blood test reference values based on medical guidelines.",
    "endpoints": {
      "GET /parameters": "List all available parameters",
      "GET /reference/{parameter}": "Get reference range for a specific parameter",
      "GET /health": "Health check endpoint",
      "GET /sse": "MCP Server-Sent Events endpoint (when MCP enabled)"
    },
    "blood_parameters_supported": 8,
    "functional_medicine_ranges": true
  }
  ```

#### 2. Health Check

- **Endpoint**: `GET /health`
- **Description**: Verify API status and connectivity
- **Response**:
  ```json
  {
    "status": "healthy",
    "book": "Der Blutwerte Coach, Naehrstoff-Therapie",
    "version": "1.0",
    "rag_enabled": true,
    "api_functional": true,
    "blood_parameters_count": 8,
    "api_endpoints": {
      "blood_test_parameters": "/parameters",
      "blood_test_reference": "/reference/{parameter}",
      "mcp_sse": "/sse"
    }
  }
  ```

#### 3. List Blood Test Parameters

- **Endpoint**: `GET /parameters`
- **Description**: Get a list of all available blood test parameters
- **Response**:
  ```json
  {
    "parameters": [
      "ferritin",
      "tsh",
      "vitamin_d",
      "vitamin_b12",
      "folate_rbc",
      "zinc",
      "magnesium",
      "selenium"
    ]
  }
  ```

#### 4. Get Reference Ranges

- **Endpoint**: `GET /reference/{parameter}`
- **Description**: Get reference ranges for a specific blood test parameter
- **Path Parameters**:
  - `parameter` (string, required): The blood test parameter (e.g., 'ferritin', 'vitamin_d')
- **Query Parameters**:
  - `sex` (string, optional): Filter by sex ('male' or 'female')
- **Response**:
  ```json
  {
    "parameter": "ferritin",
    "unit": "ng/ml",
    "optimal_range": {
      "male": {"min": 100, "max": 300},
      "female": {"min": 50, "max": 150}
    },
    "conventional_range": {
      "male": {"min": 20, "max": 500},
      "female": {"min": 10, "max": 200}
    },
    "interpretation": "Optimal ranges for general health and energy"
  }
  ```

### MCP (Model-Controller-Presenter) Endpoints

#### 1. Server-Sent Events (SSE)

- **Endpoint**: `GET /sse`
- **Description**: MCP protocol endpoint for real-time communication
- **Headers**:
  ```
  Accept: text/event-stream
  Cache-Control: no-cache
  Connection: keep-alive
  ```
- **Response**: Server-Sent Events stream

### Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing the issue"
}
```

### Example Usage

```python
import requests

# Get all available parameters
response = requests.get("http://localhost:8000/parameters")
print("Available parameters:", response.json()["parameters"])

# Get reference range for ferritin
response = requests.get(
    "http://localhost:8000/reference/ferritin",
    params={"sex": "female"}
)
print("Ferritin reference ranges:", response.json())

# Check API health
response = requests.get("http://localhost:8000/health")
print("API status:", response.json()["status"])
```

### Rate Limiting

- **Rate Limit**: 100 requests per minute per IP address
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets (UTC timestamp)

### Supported Blood Test Parameters

| Parameter    | Unit   | Description                     |
|--------------|--------|---------------------------------|
| ferritin     | ng/ml  | Iron storage protein            |
| tsh          | mIU/l  | Thyroid-stimulating hormone      |
| vitamin_d    | ng/ml  | 25-Hydroxy Vitamin D            |
| vitamin_b12  | pmol/l | Vitamin B12 (Holotranscobalamin) |
| folate_rbc   | ng/ml  | Red blood cell folate           |
| zinc         | mg/l   | Essential mineral               |
| magnesium    | mmol/l | Whole blood magnesium           |
| selenium     | µg/l   | Antioxidant mineral             |

### Technical Stack

- **Backend Framework**: FastAPI
- **Vector Database**: FAISS
- **Embeddings**: sentence-transformers
- **File Processing**: PyPDF, python-multipart
- **Containerization**: Docker
- **Deployment**: Railway, Kubernetes

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/longevitycoach/bloodtest-mcp-server.git
   cd bloodtest-mcp-server
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configuration**
   Copy the example config file and update with your settings:
   ```bash
   cp config.example.yaml config.yaml
   ```

### Development Setup

1. **Clone the repository and set up the environment**
   ```bash
   git clone <repository-url>
   cd bloodtest-mcp-server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the following variables in `.env`:
     ```
     # Environment
     ENV=development
     
     # Sentry Configuration
     SENTRY_DSN=your-sentry-dsn-here
     SENTRY_ENVIRONMENT=development
     SENTRY_TRACES_SAMPLE_RATE=1.0
     SENTRY_PROFILES_SAMPLE_RATE=1.0
     
     # Application
     APP_VERSION=1.0.0
     PORT=8002  # Default port, change if needed
     
     # Logging
     LOG_LEVEL=DEBUG
     ```

3. **Start the development server**
   ```bash
   # If using Docker (recommended)
   docker-compose up --build
   
   # Or run directly
   source venv/bin/activate
   python main.py
   ```

4. **Access the API**
   - API Base URL: http://localhost:8002
   - Swagger UI: http://localhost:8002/docs
   - ReDoc: http://localhost:8002/redoc
   - Test Sentry Error: http://localhost:8002/test-error

### Port Configuration

- The default port is set to `8002` in the `.env` file to avoid conflicts with other services.
- If you're running the server in Docker Desktop, make sure to stop any other containers that might be using the same port.
- To change the port, update the `PORT` variable in the `.env` file.

### Sentry Logging

Sentry is configured for error tracking and performance monitoring. To test Sentry logging:

1. Ensure your `SENTRY_DSN` is properly set in the `.env` file
2. Access the test error endpoint: `GET /test-error`
3. Check your Sentry dashboard for the error event

### Troubleshooting

#### Port Already in Use
If you encounter a port conflict:
```bash
# Find the process using the port
lsof -i :8002

# Kill the process (replace PID with the actual process ID)
kill -9 PID
```

#### Docker Port Conflicts
If you're using Docker Desktop and experiencing port conflicts:
1. Check running containers: `docker ps`
2. Stop conflicting containers: `docker stop <container_id>`
3. Or change the port mapping in `docker-compose.yml`

### Testing

Run the test suite with:
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest tests/

# Run with coverage report
pytest --cov=bloodtest_tools --cov-report=html tests/
```

### Deployment

#### Railway (Production)

The application is deployed on Railway and accessible at:
- **Production URL**: https://supplement-therapy.up.railway.app
- **MCP SSE Endpoint**: https://supplement-therapy.up.railway.app/sse
- **Health Check**: https://supplement-therapy.up.railway.app/health

**Deploying to Railway:**

1. **Connect Repository**
   - Connect your GitHub repository to Railway
   - Railway will auto-deploy on push to main branch

2. **Environment Variables**
   Set these in Railway dashboard:
   ```
   PORT=8000
   ENV=production
   PDF_DIRECTORY=/app/resources/books
   INDEX_DIRECTORY=/app/faiss_index
   INDEX_NAME=supplement-therapy
   ```

3. **Deployment Configuration**
   - Uses optimized Dockerfile (`Dockerfile.optimized`)
   - Includes pre-built FAISS index
   - Health check endpoint automatically monitored

4. **Monitoring**
   - View logs in Railway dashboard
   - Health endpoint: `/health`
   - Check deployment status at Railway project dashboard

#### Docker

```bash
docker build -t bloodtest-mcp-server .
docker run -p 8000:8000 bloodtest-mcp-server
```

#### Kubernetes

```bash
kubectl apply -f k8s/
```

## Technical Details

### RAG System Architecture

1. **Document Processing**
   - PDFs are split into chunks
   - Text is embedded using sentence-transformers
   - Vectors are stored in FAISS index

2. **Query Flow**
   - User query is embedded
   - Similar documents are retrieved
   - Context is passed to LLM for response generation

### 2. **MCP Protocol Tools**
- **`get_book_info`**: Returns book metadata and RAG status
- **`list_workflows`**: Available health coaching workflows
- **`supplement_therapy`**: Main personalized health coaching workflow
- **`sequential_thinking`**: Multi-step reasoning for complex health analysis
- **`search_book_knowledge`**: RAG search through indexed medical books

### 3. **RAG (Retrieval-Augmented Generation) System**
- **Vector Database**: FAISS index with sentence-transformers embeddings
- **Knowledge Base**: German medical texts on blood values and nutrition therapy
- **Books Indexed**: 
  - "Der Blutwerte-Code" by Thiemo Osterhaus
  - "Naehrstoff-Therapie" by Dr. Helena Orfanos-Boeckel
- **Search Capabilities**: Evidence-based medical knowledge retrieval

### 4. **Health Coach Workflow Engine**
- **Comprehensive Assessment**: Demographics, symptoms, lifestyle, goals
- **Blood Test Interpretation**: Optimal ranges vs lab ranges
- **Personalized Plans**: Supplement dosages, forms, timing, rationale
- **Evidence-Based**: All recommendations cited from indexed books
- **Safety Features**: Medical disclaimers, healthcare consultation requirements

### 5. **File Processing Capabilities**
- **Blood Test Uploads**: PDF and image formats
- **German Lab Reports**: Specialized parsing for German medical terminology
- **Multi-format Support**: Text, PDF, images via various processing tools

### 6. **Output Generation**
- **Structured Health Plans**: Supplement tables with dosages and timing
- **Educational Content**: Rationales with book citations
- **Dietary Recommendations**: Specific foods and preparation methods
- **Lifestyle Guidance**: Sleep, exercise, stress management

## Technical Stack Analysis

- **Framework**: FastMCP with FastAPI integration
- **AI/ML**: LangChain, sentence-transformers, FAISS
- **File Processing**: PyPDF, python-multipart
- **Configuration**: YAML-based workflow definitions
- **Authentication**: JWT with bcrypt password hashing
- **Deployment**: Docker with Railway cloud deployment

## Testing Requirements Identified

1. **API Endpoint Testing**: All 8 parameters with various input combinations
2. **MCP Tool Testing**: Each tool with success/failure scenarios  
3. **RAG System Testing**: Knowledge retrieval accuracy and relevance
4. **Workflow Testing**: Complete health coaching scenarios
5. **File Processing Testing**: Various blood test report formats
6. **Integration Testing**: End-to-end patient journey simulation
7. **Error Handling**: Edge cases, invalid inputs, system failures
8. **Performance Testing**: Concurrent requests, large file processing

---

## Table of Contents

- [🌟 Comprehensive Capabilities](#-comprehensive-capabilities)
  - [1. Blood Test Reference Values API](#1-blood-test-reference-values-api)
  - [2. MCP Protocol Tools](#2-mcp-protocol-tools)
  - [3. RAG System](#3-rag-system)
  - [4. Health Coach Workflow Engine](#4-health-coach-workflow-engine)
  - [5. File Processing Capabilities](#5-file-processing-capabilities)
  - [6. Output Generation](#6-output-generation)
- [Technical Stack](#technical-stack)
- [Testing Requirements](#testing-requirements)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [API Documentation](#api-documentation)
  - [Base URL](#base-url)
  - [Authentication](#authentication)
  - [Endpoints](#endpoints)
    - [Get API Information](#get-api-information)
    - [List Available Parameters](#list-available-parameters)
    - [Get Reference Range for a Parameter](#get-reference-range-for-a-parameter)
- [MCP Tools](#mcp-tools)
  - [Available Tools](#available-tools)
  - [Workflow Tools](#workflow-tools)
- [RAG System Setup](#rag-system-setup)
  - [Initialization](#initialization)
  - [Configuration](#rag-configuration)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Test Coverage](#test-coverage)
  - [Test Organization](#test-organization)
  - [Best Practices](#testing-best-practices)
- [Deployment](#deployment)
  - [Docker](#docker-deployment)
  - [Railway](#railway-deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Blood Test Reference Values API

TheBlood Test Reference Values API provides optimal and classical reference ranges for various blood test parameters based on medical guidelines. This API helps interpret blood test results by providing context about what values are considered optimal versus normal ranges.

### Base URL

All API endpoints are relative to the base URL of the service. For local development, this is typically `http://localhost:8000`.

### Authentication

No authentication is required for the API endpoints.

### Endpoints

#### 1. Get API Information

Returns basic information about the API and available endpoints.

- **URL**: `GET /`
- **Response**:

  ```json
  {
    "name": "Blood Test Reference Values API",
    "version": "1.0.0",
    "description": "API for retrieving optimal blood test reference values based on medical guidelines.",
    "endpoints": {
      "GET /parameters": "List all available parameters",
      "GET /reference/{parameter}": "Get reference range for a specific parameter"
    }
  }
  ```

#### 2. List Available Parameters

Returns a list of all available blood test parameters with their units.

- **URL**: `GET /parameters`
- **Response**:

  ```json
  {
    "parameters": [
      {
        "parameter": "ferritin",
        "unit": "ng/ml"
      },
      {
        "parameter": "tsh",
        "unit": "mIU/l"
      },
      {
        "parameter": "vitamin_d",
        "unit": "ng/ml"
      },
      {
        "parameter": "vitamin_b12",
        "unit": "pmol/l"
      },
      {
        "parameter": "folate_rbc",
        "unit": "ng/ml"
      },
      {
        "parameter": "zinc",
        "unit": "mg/l"
      },
      {
        "parameter": "magnesium",
        "unit": "mmol/l"
      },
      {
        "parameter": "selenium",
        "unit": "µg/l"
      }
    ]
  }
  ```

#### 3. Get Reference Range for a Parameter

Returns the reference range information for a specific blood test parameter.

- **URL**: `GET /reference/{parameter}`
- **Query Parameters**:
  - `sex` (optional): Filter results by sex ("male" or "female") for sex-specific ranges
- **Response**:

  ```json
  {
    "parameter": "ferritin",
    "unit": "ng/ml",
    "optimal_range": "70–200 (optimal)",
    "classical_range": "15-400 depending on sex and age",
    "explanation": "Iron storage protein; reflects total body iron stores. Low levels indicate iron deficiency before anemia develops. High levels may indicate inflammation, infection, or iron overload conditions.",
    "sex_specific": true,
    "sex_specific_range": "premenopausal: 15–150, postmenopausal: 15–300, optimal: 70–200"
  }
  ```

- **Error Responses**:
  - `404 Not Found`: If the specified parameter is not found
  - `422 Unprocessable Entity`: If the sex parameter is invalid

### Example Usage

#### Using cURL

```bash
# Get API information
curl http://localhost:8000/

# List all available parameters
curl http://localhost:8000/parameters

# Get reference range for ferritin
curl http://localhost:8000/reference/ferritin

# Get sex-specific reference range for ferritin (female)
curl "http://localhost:8000/reference/ferritin?sex=female"
```

#### Using Python

```python
import requests

# Get API information
response = requests.get("http://localhost:8000/")
print(response.json())

# List all available parameters
response = requests.get("http://localhost:8000/parameters")
parameters = response.json()["parameters"]
print(f"Available parameters: {[p['parameter'] for p in parameters]}")

# Get reference range for ferritin
response = requests.get("http://localhost:8000/reference/ferritin")
print(f"Ferritin reference range: {response.json()['optimal_range']}")

# Get sex-specific reference range for ferritin (female)
response = requests.get(
    "http://localhost:8000/reference/ferritin",
    params={"sex": "female"}
)
print(f"Female ferritin reference range: {response.json()['sex_specific_range']}")
```

### Extending the Reference Values

To add or modify reference values, edit the `reference_values.py` file in the `bloodtest_tools` package. The reference values are stored in a dictionary where each key is a parameter name and the value is a `ReferenceRange` object.

Example:

```python
REFERENCE_VALUES = {
    "ferritin": ReferenceRange(
        parameter="ferritin",
        unit="ng/ml",
        optimal_range="70–200 (optimal)",
        classical_range="15-400 depending on sex and age",
        explanation=(
            "Iron storage protein; reflects total body iron stores. "
            "Low levels indicate iron deficiency before anemia develops. "
            "High levels may indicate inflammation, infection, or iron overload conditions."
        ),
        sex_specific=True,
        sex_specific_ranges={
            "MALE": "15–300, optimal: 70–200",
            "FEMALE": "premenopausal: 15–150, postmenopausal: 15–300, optimal: 70–200"
        }
    ),
    # ... other parameters
}
```

## MCP Tools for Blood Test Reference Values

The Blood Test MCP Server provides a comprehensive set of tools for programmatic access to blood test reference values. These tools can be used within the MCP framework to retrieve and process blood test information.

### Available Tools

#### 1. BloodTestTool

The `BloodTestTool` class provides methods to interact with blood test reference values.

##### Methods

###### `get_optimal_values(parameter: str, sex: Optional[str] = None) -> Dict[str, Any]`

Retrieves the optimal and classical reference ranges for a specific blood test parameter.

**Parameters:**
- `parameter` (str): The name of the blood test parameter (case-insensitive).
- `sex` (str, optional): The sex of the patient ('male' or 'female') for sex-specific ranges.

**Returns:**
A dictionary containing the parameter details, including optimal and classical ranges, units, and explanations.

**Raises:**
- `HTTPException`: If the parameter is not found or if an invalid sex is provided.

**Example:**
```python
# Get reference values for ferritin
tool = BloodTestTool()
result = tool.get_optimal_values("ferritin")

# Get sex-specific reference values
female_values = tool.get_optimal_values("ferritin", "female")
```

###### `list_parameters() -> List[Dict[str, str]]`

Lists all available blood test parameters and their units.

**Returns:**
A list of dictionaries, each containing 'parameter' and 'unit' keys.

**Example:**
```python
# List all available parameters
tool = BloodTestTool()
parameters = tool.list_parameters()
```

### Integration with MCP

The BloodTestTool can be registered with an MCP server to make it available for use in MCP workflows:

```python
from mcp import MCP
from bloodtest_tools.mcp_tool import BloodTestTool

# Create MCP instance
mcp = MCP()

# Register the BloodTestTool
mcp.register_tool(BloodTestTool())

# Now the tool can be used in MCP workflows
```

## Testing

### Running Tests

The test suite includes unit tests for the core functionality and integration tests for the API endpoints.

#### Running All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=bloodtest_tools tests/
```

#### Running Specific Test Files

```bash
# Run API endpoint tests
pytest tests/test_api_endpoints.py -v

# Run core functionality tests
pytest tests/test_bloodtest_tools.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

### Test Coverage

To generate a test coverage report:

```bash
# Install coverage if not already installed
pip install pytest-cov

# Run tests with coverage
pytest --cov=bloodtest_tools --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=bloodtest_tools --cov-report=html tests/
# Open htmlcov/index.html in your browser
```

### Writing Tests

When adding new features or fixing bugs, please add corresponding tests. Follow these guidelines:

1. Test files should be named `test_*.py` or `*_test.py`
2. Test functions should start with `test_`
3. Use descriptive test function names that describe what's being tested
4. Test both success and error cases
5. Mock external dependencies when appropriate

Example test:

```python
def test_get_optimal_values_valid_parameter():
    """Test getting optimal values for a valid parameter."""
    tool = BloodTestTool()
    result = tool.get_optimal_values("ferritin")
    assert "optimal_range" in result
    assert result["parameter"] == "ferritin"
```

## Health Check Endpoint

The server provides a health check endpoint at `/health` that returns the current status of the service:

```json
{
  "status": "healthy",
  "book": "Der Blutwerte Coach, Naehrstoff-Therapie",
  "version": "1.0",
  "rag_enabled": true
}
```

## MCP Capabilities

The MCP server provides several tools and workflows that can be accessed through the MCP protocol. Below is a comprehensive list of available capabilities:

### Generic Tools

1. **get_book_info**
   - **Description**: Returns metadata about the currently loaded book and available workflows.
   - **Returns**: JSON object containing book title, author, domain, description, available workflows, and RAG status.
   - **Example Response**:
     ```json
     {
       "title": "Der Blutwerte Coach, Naehrstoff-Therapie",
       "author": "Author Name",
       "domain": "Health and Nutrition",
       "description": "Detailed book description",
       "available_workflows": ["Supplement Therapy"],
       "rag_enabled": true
     }
     ```

2. **list_workflows**
   - **Description**: Lists all available workflows with their names and descriptions.
   - **Returns**: Array of workflow objects.
   - **Example Response**:
     ```json
     [
       {
         "name": "Supplement Therapy",
         "description": "Provides personalized supplement recommendations based on blood test results"
       }
     ]
     ```

### Workflow Tools

Workflow tools are dynamically generated based on the configuration in `structure.yaml`. Each workflow becomes an MCP tool with a name derived from the workflow name (converted to snake_case).

1. **supplement_therapy** (Example)
   - **Description**: Executes the Supplement Therapy workflow.
   - **Returns**: The final prompt or result of the workflow execution.
   - **Note**: The actual workflow name and parameters depend on your `structure.yaml` configuration.

### Advanced Tools

1. **sequential_thinking**
   - **Description**: Enables multi-step reasoning and thought processes for complex problem-solving.
   - **Parameters**:
     - `thought` (str): Current thinking step
     - `thought_number` (int): Current thought number (1-based)
     - `total_thoughts` (int): Estimated total thoughts needed
     - `next_thought_needed` (bool): Whether another thought step is needed
     - `is_revision` (bool, optional): Whether this revises previous thinking
     - `revises_thought` (int, optional): Which thought is being reconsidered
   - **Returns**: JSON response with thought processing status.

2. **rag_search** (Available if RAG is enabled)
   - **Description**: Performs retrieval-augmented generation search against the book's knowledge base.
   - **Parameters**:
     - `query` (str): The search query
     - `k` (int, optional): Number of results to return (default: 5)
   - **Returns**: Relevant passages from the knowledge base.

### HTTP Endpoints

1. **GET /health**
   - **Description**: Health check endpoint
   - **Response**: JSON with service status
   - **Example**: `curl http://localhost:8000/health`

2. **GET /sse**
   - **Description**: Server-Sent Events (SSE) transport endpoint for MCP clients
   - **Usage**: Used by MCP clients to establish a persistent connection

### Authentication

All MCP tools require proper authentication via the MCP protocol. Ensure your client is properly configured with valid credentials before making requests.

## Resource Directory Structure

- `/resources/` - Contains all book resources and PDFs
  - `books/` - Books in PDF format used by the RAG system
- `/faiss_index/` - Contains the FAISS vector index files
- `/scripts/` - Utility scripts for the application

## 1. Local Development Setup

Follow these steps to set up and run the project on your local machine.

### a. Local Prerequisites

- Python 3.9 or higher.
- `pip` and `venv` (usually included with Python).

### b. Create and Activate Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# Navigate to the project root directory
cd /path/to/Bloodtest-mcp-server

# Create a virtual environment (e.g., named .venv)
python3 -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### c. Install Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

### d. Initialize the RAG Knowledge Base

The `scripts/init_rag.py` script processes your PDF documents, creates embeddings, and stores them in a FAISS vector index. This script uses environment variables for configuration:

- `PDF_DIRECTORY`: Path to the directory containing your PDF files (default: `/app/resources/books` in Docker, `resources/books` locally).
- `INDEX_NAME`: The desired name for your FAISS index (e.g., `supplement-therapy`). This **must** match the `index_name` in `structure.yaml`.
- `INDEX_DIRECTORY`: Directory where the FAISS index will be saved (defaults to `faiss_index`).
- `FORCE_REINDEX`: Set to `true` to force re-indexing even if an index with the same name exists (defaults to `false`).

**Example command to run the script locally:**

```bash
# Ensure your virtual environment is active
# Make sure your PDFs are in the 'resources/books' directory
sh -c 'source .venv/bin/activate && INDEX_NAME="supplement-therapy" PDF_DIRECTORY="resources/books" python scripts/init_rag.py'
```

**Note:** The Docker image comes pre-built with the FAISS index, so manual initialization is typically not needed.

This will create files like `faiss_index/supplement-therapy.faiss` and `faiss_index/supplement-therapy_hashes.json`.

### e. Customize AI Behavior (`books/structure.yaml`)

The AI's behavior is defined in `books/structure.yaml`. Adapt this file to your specific domain and the content of your indexed books. Critically, ensure the `rag.config.index_name` in this file matches the `INDEX_NAME` you used during RAG initialization.

```yaml
# ... other configurations ...
rag:
  enabled: true
  config:
    index_name: "supplement-therapy" # <-- MUST MATCH YOUR INDEX_NAME
    index_directory: "./faiss_index"
# ... other configurations ...
```

Refer to the comments within `structure.yaml` or previous discussions for details on customizing `<ROLE>`, `<INPUT_NEEDED>`, `<PROCESS>`, etc.

### f. Run the MCP Server Locally

Once the RAG is initialized and `structure.yaml` is configured, start the MCP server:

```bash
# Ensure your virtual environment is active
python server.py --host 0.0.0.0 --port 8000
```

The server will start (defaulting to `http://0.0.0.0:8000`), load the FAISS index, and expose the configured MCP tools. You can access the following endpoints:

- `http://localhost:8000/health` - Health check endpoint
- `http://localhost:8000/sse` - SSE transport endpoint for MCP clients

## 2. Docker Setup

Docker can simplify deployment by packaging the application and its dependencies. The Docker image is pre-configured with all necessary dependencies and the FAISS index.

### a. Prerequisites

- Docker Engine
- Docker Compose (optional, for `docker-compose` commands)

### b. Building the Docker Image

To build the optimized Docker image, run:

```bash
docker build -t bloodtest-mcp-server -f Dockerfile.optimized .
```

### c. Running the Docker Container

To run the container with the built image:

```bash
docker run -d \
  -p 8000:8000 \
  --name bloodtest-mcp-server \
  -e PORT=8000 \
  -e ENV=DEV \
  bloodtest-mcp-server
```

This will:
1. Start the container in detached mode (`-d`)
2. Map port 8000 on your host to port 8000 in the container
3. Set the container name to `bloodtest-mcp-server`
4. Set the port and environment variables
5. Use the `bloodtest-mcp-server` image we built

### d. Verifying the Deployment

Once the container is running, you can verify the health check endpoint:

```bash
curl http://localhost:8000/health
```

You should see a response like:

```json
{
  "status": "healthy",
  "book": "Der Blutwerte Coach, Naehrstoff-Therapie",
  "version": "1.0",
  "rag_enabled": true
}
```

### e. Stopping and Removing the Container

To stop the container:

```bash
docker stop bloodtest-mcp-server
```

To remove the container (after stopping it):

```bash
docker rm bloodtest-mcp-server
```

### f. Viewing Logs

To view the container logs:

```bash
docker logs bloodtest-mcp-server
```

For following the logs in real-time:

```bash
docker logs -f bloodtest-mcp-server
```

## 3. Troubleshooting

### Common Issues and Solutions

#### 1. Connection Reset When Accessing Endpoints

**Symptom**: You see a "Connection reset by peer" error when trying to access the health check or other endpoints.

**Solution**:
- Ensure the container is running: `docker ps`
- Check the container logs for errors: `docker logs bloodtest-mcp-server`
- Verify the server is binding to `0.0.0.0` (not `127.0.0.1`) in the container
- Make sure the port mapping is correct (e.g., `-p 8000:8000`)

#### 2. Configuration File Not Found

**Symptom**: Errors about missing `structure.yaml` or other configuration files.

**Solution**:
- Verify the file exists in the correct location (`/app/resources/structure.yaml` in the container)
- Check file permissions: `docker exec -it bloodtest-mcp-server ls -la /app/resources/`
- Ensure the file was included in the Docker build (check `.dockerignore`)

#### 3. FAISS Index Loading Issues

**Symptom**: Errors about missing or invalid FAISS index files.

**Solution**:
- Verify the FAISS index files exist in the container: `docker exec -it bloodtest-mcp-server ls -la /app/faiss_index/`
- Check that the `index_name` in `structure.yaml` matches the FAISS index filename
- Ensure the files have the correct permissions

#### 4. Container Fails to Start

**Symptom**: The container exits immediately after starting.

**Solution**:
- Check the logs: `docker logs bloodtest-mcp-server`
- Try running interactively: `docker run -it --rm bloodtest-mcp-server /bin/bash`
- Verify all required environment variables are set

#### 5. Health Check Fails

**Symptom**: The `/health` endpoint returns an error or is not accessible.

**Solution**:
- Check if the server is running: `docker ps`
- Look for errors in the logs: `docker logs bloodtest-mcp-server`
- Verify the port mapping is correct
- Check if another service is using the same port

## Testing

This project includes a comprehensive test suite to ensure the reliability and correctness of the Blood Test Reference Values API and MCP tools. The tests are organized into several categories to provide thorough coverage.

### Test Organization

The test suite is organized as follows:

- `tests/test_api_endpoints.py`: Tests for the FastAPI endpoints
- `tests/test_bloodtest_tools.py`: Unit tests for the BloodTestTool class and core functions
- `tests/test_edge_cases.py`: Tests for edge cases and error conditions
- `tests/test_integration.py`: Integration tests and workflow simulations

### Running Tests

To run the entire test suite:

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_api_endpoints.py -v

# Run a specific test function
pytest tests/test_api_endpoints.py::test_root_endpoint -v
```

### Test Coverage

To generate a test coverage report:

```bash
# Install coverage if not already installed
pip install pytest-cov

# Run tests with coverage
pytest --cov=bloodtest_tools tests/

# Generate HTML report
pytest --cov=bloodtest_tools --cov-report=html tests/
open htmlcov/index.html  # View the report in your browser
```

### MCP Tool Testing

The MCP tool is thoroughly tested with various scenarios:

1. **Basic Functionality**
   - Retrieving reference values for valid parameters
   - Handling sex-specific reference ranges
   - Listing available parameters

2. **Error Handling**
   - Invalid parameter names
   - Invalid sex values
   - Empty or malformed requests

3. **Edge Cases**
   - Very long parameter names
   - Special characters in parameter names
   - Case sensitivity
   - Concurrent API requests
   - None/Null values

### Example Test Cases

```python
def test_get_reference_range_valid_parameter():
    """Test getting reference range for a valid parameter."""
    result = get_reference_range("ferritin")
    assert result["parameter"] == "ferritin"
    assert result["unit"] == "ng/ml"
    assert result["sex_specific"] is True

def test_edge_case_long_parameter_name():
    """Test with very long parameter names."""
    long_param = "a" * 1000
    with pytest.raises(ValueError):
        get_reference_range(long_param)

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
```

### Continuous Integration

This project includes a GitHub Actions workflow (`.github/workflows/tests.yml`) that runs the test suite on every push and pull request. The workflow:

1. Sets up Python
2. Installs dependencies
3. Runs the test suite with coverage
4. Uploads coverage results to Codecov

### Testing Best Practices

1. **Isolation**: Each test should be independent and not rely on the state from other tests.
2. **Descriptive Names**: Test functions should have clear, descriptive names that explain what they're testing.
3. **Edge Cases**: Always test edge cases, including:
   - Empty inputs
   - Boundary values
   - Invalid inputs
   - Error conditions
4. **Mocking**: Use mocking for external dependencies when appropriate.
5. **Documentation**: Document the purpose of each test and any assumptions made.

### MCP Tool Usage Examples

Here are some examples of how to use the BloodTestTool MCP tool:

```python
from bloodtest_tools.mcp_tool import BloodTestTool

# Initialize the tool
tool = BloodTestTool()

# Get reference values for a parameter
result = tool.get_optimal_values("ferritin", "female")
print(f"Optimal range for ferritin (female): {result['optimal_range']}")

# List all available parameters
parameters = tool.list_parameters()
print(f"Available parameters: {[p['parameter'] for p in parameters]}")

# Handle errors
try:
    result = tool.get_optimal_values("invalid_parameter")
except HTTPException as e:
    print(f"Error: {e.detail}")
```

### API Testing Examples

You can test the API using `curl` or any HTTP client:

```bash
# Get API information
curl http://localhost:8000/

# List all parameters
curl http://localhost:8000/parameters

# Get reference range for ferritin
curl "http://localhost:8000/reference/ferritin?sex=female"
```

### Performance Testing

The test suite includes performance tests to ensure the API can handle concurrent requests efficiently. These tests verify that:

1. Response times remain acceptable under load
2. The system handles concurrent requests correctly
3. No data corruption occurs during concurrent access

To run performance tests:

```bash
pytest tests/test_performance.py -v
```

### Testing with Docker

To run tests in a Docker container:

```bash
# Build the test image
docker build --target test -t bloodtest-tests .

# Run tests
docker run --rm bloodtest-tests
```

### Debugging Tests

If a test fails, you can use the following techniques to debug:

1. Run with `-s` to see print statements:
   ```bash
   pytest tests/test_file.py -v -s
   ```

2. Use `pdb` to set breakpoints:
   ```python
   import pdb; pdb.set_trace()
   ```

3. Check the test coverage report to identify untested code paths.

### Test Maintenance

To keep the test suite maintainable:

1. Update tests when adding new features or fixing bugs
2. Remove or update obsolete tests
3. Keep test data in a consistent state
4. Document any test dependencies

### Getting Help

If you encounter issues not covered here:

1. Check the container logs: `docker logs bloodtest-mcp-server`
2. Verify the container is running: `docker ps`
3. Check for error messages in the logs
4. Ensure all dependencies are installed and up to date
5. Check file permissions and paths

## 4. Docker Compose Setup (Alternative)

For a more production-like setup, you can use Docker Compose:

### a. Docker Prerequisites

- Docker Engine
- Docker Compose

### b. Configure `docker-compose.yml`

Review and adjust `docker-compose.yml`. Key environment variables for the `app` service that affect RAG initialization:

- `PDF_DIRECTORY`: Path to the PDFs inside the container (default: `/app/resources/books`)
- `INDEX_DIRECTORY`: Directory containing the FAISS index (default: `/app/faiss_index`)
- `INDEX_NAME`: Name of the FAISS index (must match `structure.yaml`)
- `INDEX_NAME`: Set this to your desired index name (e.g., `supplement-therapy`). This is passed to `init_rag.py`.
- `INDEX_DIRECTORY`: Path *inside the container* for the FAISS index (e.g., `/app/faiss_index`).
- `FORCE_REINDEX`: Set to `false` or `true`.

```yaml
services:
  app:
    # ... other docker compose configurations ...
    environment:
      - PYTHONUNBUFFERED=1
      - ENV=PRODUCTION
      - PDF_DIRECTORY=/app/resources  # PDFs are mounted here from ./resources
      - INDEX_NAME=supplement-therapy # Matches structure.yaml
      - INDEX_DIRECTORY=/app/faiss_index
      - FORCE_REINDEX=false
    # The command already runs init_rag.py then server.py
    command: sh -c "python scripts/init_rag.py && python server.py"
```

Ensure your local PDF directory (e.g., `./resources`) and FAISS index directory (e.g., `./faiss_index`) are correctly mounted as volumes.

### c. Build and Run with Docker Compose

From the project root directory:

```bash
docker-compose up --build -d
```

This command will:

1. Build the Docker image (if not already built or if Dockerfile changed).
2. Create and start the container(s) in detached mode (`-d`).
3. The `command` in `docker-compose.yml` will first run `scripts/init_rag.py` (using the environment variables set in `docker-compose.yml`) and then start `server.py`.

### d. Accessing the Server

The server running inside Docker will be accessible based on the port mapping in `docker-compose.yml` (e.g., `8000:8000` makes it available at `http://localhost:8000`).

#### Endpoints

- `http://localhost:8000/health` - Health check endpoint
- `http://localhost:8000/sse` - SSE transport endpoint for MCP clients

### e. Deploying to Railway

The application is configured for deployment to Railway. The deployment includes:

- Pre-built Docker image with all dependencies
- FAISS index pre-loaded
- Health check endpoint at `/health`
- SSE transport at `/sse`

To deploy:

1. Push your changes to the repository connected to Railway
2. Railway will automatically build and deploy the application
3. The health check will run automatically to verify the deployment

#### Environment Variables in Railway

- `PORT`: The port the server should listen on (set by Railway)
- `PDF_DIRECTORY`: Path to PDFs (default: `/app/resources/books`)
- `INDEX_DIRECTORY`: Path to FAISS index (default: `/app/faiss_index`)
- `INDEX_NAME`: Name of the FAISS index (must match `structure.yaml`)

## 3. Deployment with Railway CLI

You can also deploy this project to [Railway](https://railway.app/) using their command-line interface.

### a. Railway CLI Prerequisites

- Install the Railway CLI. Instructions can be found [here](https://docs.railway.app/develop/cli#installation).

### b. Login to Railway

Authenticate the CLI with your Railway account:

```bash
railway login
```

### c. Link to Your Railway Project

Navigate to your local project's root directory and link it to your existing Railway project and service:

```bash
cd /path/to/Bloodtest-mcp-server
railway link
```

Follow the prompts to select the appropriate project and service. If you haven't created a project/service on Railway yet, do so through their web dashboard first.

### d. Deploy

Once linked, deploy your project:

```bash
railway up
```

This command will build and deploy your application based on your Railway project settings (e.g., if it uses a Dockerfile or Nixpacks). The `command` specified in your `docker-compose.yml` ( `sh -c "python scripts/init_rag.py && python server.py"`) or a similar start command in your Railway service settings will be used to initialize the RAG index and start the server.

## Blood Test Reference Values API

This service includes a comprehensive API for retrieving optimal blood test reference values based on medical guidelines from Dr. Ulrich Strunz and Dr. med. Helena Orfanos-Boeckel.

### Available Endpoints

#### List Available Parameters
```
GET /api/bloodtest/parameters
```

Returns a list of all available blood test parameters with their units.

Example response:
```json
{
  "parameters": [
    {"parameter": "ferritin", "unit": "ng/ml"},
    {"parameter": "tsh", "unit": "mIU/l"},
    {"parameter": "vitamin_d", "unit": "ng/ml"},
    ...
  ]
}
```

#### Get Reference Range
```
GET /api/bloodtest/reference/{parameter}
```

Get the reference range for a specific blood test parameter.

**Query Parameters:**
- `sex` (optional): Filter by sex (`male` or `female`)

Example request:
```
GET /api/bloodtest/reference/ferritin?sex=female
```

Example response:
```json
{
  "parameter": "ferritin",
  "unit": "ng/ml",
  "optimal_range": "70–200 (optimal)",
  "classical_range": "15-400 depending on sex and age",
  "explanation": "Iron storage protein; reflects total body iron stores...",
  "sex_specific": true,
  "sex_specific_range": "premenopausal: 15–150, postmenopausal: 15–300, optimal: 70–200"
}
```

### Integration with Existing Workflow

The Blood Test Reference Values API is automatically integrated into the existing health coach workflow. When processing blood test results, the system will:

1. Identify the test parameters in the results
2. Retrieve optimal reference values for each parameter
3. Include these reference values in the analysis and recommendations

### Available Parameters

The following blood test parameters are currently supported:

| Parameter | Unit | Description |
|-----------|------|-------------|
| ferritin | ng/ml | Iron storage protein |
| tsh | mIU/l | Thyroid-stimulating hormone |
| vitamin_d | ng/ml | 25-OH Vitamin D |
| vitamin_b12 | pmol/l | Vitamin B12 (Holo-TC) |
| folate_rbc | ng/ml | Red Blood Cell Folate |
| zinc | mg/l | Zinc |
| magnesium | mmol/l | Magnesium (whole blood) |
| selenium | µg/l | Selenium |

### Development

To add new parameters or modify existing reference values, update the `REFERENCE_VALUES` dictionary in `bloodtest_tools/reference_values.py`.

#### Running Tests

```bash
pytest tests/test_bloodtest_tools.py -v
```

#### Code Style

This project uses `black` for code formatting and `flake8` for linting.

```bash
# Format code
black .

# Run linter
flake8
```

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

- Reference values are based on the work of Dr. Ulrich Strunz and Dr. med. Helena Orfanos-Boeckel.
- Built with [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://pydantic-docs.helpmanual.io/), and [Uvicorn](https://www.uvicorn.org/).

## 4. Testing with an MCP Client

A simple Python script, `client_test.py` (located in the project root), can be used to interact with the running MCP server. See the script for an example of how to connect and call a tool.

The MCP server provides an SSE (Server-Sent Events) endpoint for client connections.

- When running locally (or via Docker mapped to localhost), the endpoint is: `http://localhost:8000/sse`
- When deployed to Railway, the endpoint will be: `http://supplement-therapy.up.railway.app/sse` (or your specific generated Railway domain)

You'll need to update the `SERVER_URL` in `client_test.py` accordingly.

```bash
# Ensure the server is running (either locally or in Docker)
# If running locally, ensure your virtual environment is active for the client too, or that 'mcp' is globally available.
source .venv/bin/activate # If applicable
python client_test.py
```

## 5. Features

- Dynamic tool generation from book YAML config
- FastMCP-based server
- Easily extensible for any book or methodology
- Dockerized for easy deployment

## 6. Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

## 7. Quick Start

1. **Clone the repository**

   ```sh
   git clone git@github.com:longevitycoach/bloodtest-mcp-server.git
   cd bloodtest-mcp-server
   ```

2. **Build and run with Docker Compose**

   ```sh
   docker-compose up --build
   ```

   The server will be available at [http://127.0.0.1:8000](http://localhost:8000)

3. **Configuration**

   - An example configuration file is `gtd.yaml` (or any other YAML files).
   - You can mount your own config or edit the existing one.

4. **Initialize the RAG System**

   To build the knowledge base from your own documents, follow these steps:

   a. **Add Your PDFs**
      Place all your PDF files in the `scripts/pdfs/` directory.

   b. **Run the Initialization Script**
      Execute the following command to index the PDFs and create the FAISS index. If you are using a virtual environment, make sure it is activated first.

      ```sh
      python3 scripts/init_rag.py
      ```

## 8. Development

- The code is mounted as a volume in the container, so changes are reflected immediately (except for dependency changes).
- To install new dependencies, update `pyproject.toml` or use uv and rebuild the image.

## Project Structure

- `server.py` - Main server code
- `gtd.yaml` - Example book configuration (GTD methodology)
- `Dockerfile` - Container build instructions
- `docker-compose.yml` - Multi-container orchestration
- `pyproject.toml` - Python dependencies

## Example Endpoints

- The server exposes methods and concepts as API tools based on the loaded book config.
