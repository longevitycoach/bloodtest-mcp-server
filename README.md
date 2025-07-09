# Bloodtest MCP Server

A comprehensive health coaching system that combines blood test analysis with evidence-based nutritional therapy recommendations, powered by Retrieval-Augmented Generation (RAG) technology.

**🔗 Live Endpoint**: [https://bloodtest-mcp.up.railway.app](https://bloodtest-mcp.up.railway.app)

## Table of Contents

- [Overview](#overview)
  - [Key Features](#key-features)
  - [Technical Stack](#technical-stack)
- [User Manual](#user-manual)
  - [Getting Started](#getting-started)
  - [Claude Desktop Integration](#claude-desktop-integration)
  - [Using the Health Coach](#using-the-health-coach)
  - [Available MCP Tools](#available-mcp-tools)
- [Developer Manual](#developer-manual)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Development Setup](#development-setup)
  - [API Documentation](#api-documentation)
  - [Testing](#testing)
  - [Deployment](#deployment)
  - [Project Structure](#project-structure)
- [Advanced Topics](#advanced-topics)
  - [RAG System Architecture](#rag-system-architecture)
  - [Workflow Configuration](#workflow-configuration)
  - [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

### Key Features

- **Blood Test Analysis**: Get optimal ranges for 8+ key health markers based on functional medicine
- **Personalized Recommendations**: Evidence-based supplement and lifestyle advice from German medical literature
- **RAG-Powered Knowledge Base**: Search through indexed medical texts using FAISS vector database
- **MCP Protocol Support**: Integrate with Claude Desktop and other MCP-compatible clients
- **Multi-format Support**: Process blood test results in PDF, image, and text formats
- **RESTful API**: Access blood test reference values programmatically
- **Health Coaching Workflows**: Comprehensive assessment and recommendation generation

### Technical Stack

- **Framework**: FastMCP with FastAPI integration
- **AI/ML**: LangChain, sentence-transformers, FAISS
- **File Processing**: PyPDF, python-multipart
- **Configuration**: YAML-based workflow definitions
- **Deployment**: Docker with Railway cloud deployment
- **Language**: Python 3.12+

## User Manual

### Getting Started

1. **Access the Production System**
   - Web Interface: [https://bloodtest-mcp.up.railway.app](https://bloodtest-mcp.up.railway.app)
   - API Base URL: `https://bloodtest-mcp.up.railway.app`
   - MCP SSE Endpoint: `https://bloodtest-mcp.up.railway.app/sse`
   - Health Check: `https://bloodtest-mcp.up.railway.app/health`
   
   **Legacy URL** (still active): `https://supplement-therapy.up.railway.app`

2. **Authentication**
   - Currently, no authentication is required for public endpoints
   - For production use, implement Bearer token authentication

### Claude Desktop Integration

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
           "https://bloodtest-mcp.up.railway.app/sse"
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

### Using the Health Coach

1. **Upload Blood Test Results**
   - Supported formats: PDF, JPG, PNG
   - German lab reports are automatically parsed
   - Optimal ranges are compared against your results

2. **Complete Health Assessment**
   - Provide demographic information
   - Describe current symptoms and health concerns
   - Set your health goals and priorities

3. **Receive Personalized Recommendations**
   - Supplement protocols with specific dosages and timing
   - Dietary modifications based on your deficiencies
   - Lifestyle interventions for optimal health
   - All recommendations include citations from medical literature

### Available MCP Tools

1. **`get_book_info`**
   - Returns metadata about loaded medical books and RAG status
   - Shows available workflows and system capabilities

2. **`list_workflows`**
   - Lists all available health coaching workflows
   - Each workflow has a specific focus area

3. **`supplement_therapy`**
   - Main health coaching workflow
   - Provides comprehensive supplement recommendations
   - Requires patient assessment data

4. **`search_book_knowledge`**
   - Search through indexed medical knowledge base
   - Returns relevant passages with page references
   - Example: "optimal ferritin levels for women"

5. **`sequential_thinking`**
   - Multi-step reasoning for complex health analysis
   - Useful for differential diagnosis and complex cases

## Developer Manual

### Prerequisites

- Python 3.12 or higher
- Docker (optional, for containerized deployment)
- Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/longevitycoach/bloodtest-mcp-server.git
   cd bloodtest-mcp-server
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Development Setup

1. **Initialize the RAG Knowledge Base**
   ```bash
   # Place PDF files in resources/books directory
   INDEX_NAME="supplement-therapy" PDF_DIRECTORY="resources/books" python scripts/init_rag.py
   ```

2. **Configure the Application**
   - Edit `resources/structure.yaml` to customize workflows
   - Ensure `rag.config.index_name` matches your INDEX_NAME

3. **Run the Development Server**
   ```bash
   # Run MCP server with SSE transport
   python server.py --host 0.0.0.0 --port 8000

   # Or run integrated server (MCP + API)
   python integrated_server.py --host 0.0.0.0 --port 8000

   # Or run just the FastAPI server
   python main.py
   ```

### API Documentation

#### Base Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint
- `GET /parameters` - List all blood test parameters
- `GET /reference/{parameter}` - Get reference range for a parameter
- `GET /sse` - MCP Server-Sent Events endpoint

#### Example API Usage

```python
import requests

# Get all available parameters
response = requests.get("https://bloodtest-mcp.up.railway.app/parameters")
print("Available parameters:", response.json()["parameters"])

# Get reference range for ferritin
response = requests.get(
    "https://bloodtest-mcp.up.railway.app/reference/ferritin",
    params={"sex": "female"}
)
print("Ferritin reference:", response.json())
```

#### Blood Test Parameters Supported

| Parameter | Unit | Description |
|-----------|------|-------------|
| ferritin | ng/ml | Iron storage protein |
| tsh | mIU/l | Thyroid-stimulating hormone |
| vitamin_d | ng/ml | 25-OH Vitamin D |
| vitamin_b12 | pmol/l | Vitamin B12 (Holo-TC) |
| folate_rbc | ng/ml | Red Blood Cell Folate |
| zinc | mg/l | Essential mineral |
| magnesium | mmol/l | Whole blood magnesium |
| selenium | µg/l | Antioxidant mineral |

### Testing

```bash
# Run all tests with coverage
pytest tests/ -v --cov=bloodtest_tools --cov-report=term-missing

# Run specific test file
pytest tests/test_api_endpoints.py -v

# Run with Makefile
make test
```

#### Test Organization

- `tests/test_api_endpoints.py` - API endpoint tests
- `tests/test_bloodtest_tools.py` - Core functionality tests
- `tests/test_edge_cases.py` - Edge case handling
- `tests/test_integration.py` - Integration tests
- `testdata/` - Comprehensive test scenarios and data

### Deployment

#### Railway (Production)

The application is deployed on Railway:

1. **Connect Repository**
   - Connect GitHub repository to Railway
   - Auto-deploys on push to main branch

2. **Environment Variables**
   ```
   PORT=8000
   ENV=production
   PDF_DIRECTORY=/app/resources/books
   INDEX_DIRECTORY=/app/faiss_index
   INDEX_NAME=supplement-therapy
   ```

3. **Monitoring**
   - Health check: https://bloodtest-mcp.up.railway.app/health
   - View logs in Railway dashboard
   - Public endpoint: https://bloodtest-mcp.up.railway.app

#### Docker

```bash
# Build and run with Docker
docker build -t bloodtest-mcp-server -f Dockerfile.optimized .
docker run -p 8000:8000 bloodtest-mcp-server

# Or use Docker Compose
docker-compose up --build
```

### Project Structure

```
bloodtest-mcp-server/
├── bloodtest_tools/        # Core blood test functionality
│   ├── api.py             # FastAPI endpoints
│   ├── reference_values.py # Medical reference ranges
│   └── mcp_tool.py        # MCP tool wrappers
├── utils/                  # Utility modules
│   ├── rag_system.py      # FAISS RAG implementation
│   └── sequential_thinking.py # Reasoning tool
├── resources/              # Configuration and books
│   ├── structure.yaml     # Workflow definitions
│   └── books/             # PDF medical texts
├── scripts/               # Utility scripts
│   └── init_rag.py       # RAG initialization
├── tests/                 # Test suite
├── server.py             # Main MCP server
├── integrated_server.py  # Combined MCP + API server
└── main.py              # FastAPI entry point
```

## Advanced Topics

### RAG System Architecture

1. **Document Processing**
   - PDFs are split into chunks (1000 chars with 200 overlap)
   - Text embedded using sentence-transformers
   - Vectors stored in FAISS index

2. **Query Flow**
   - User query is embedded
   - Top-k similar documents retrieved
   - Context passed to LLM for response generation

3. **Configuration**
   ```yaml
   rag:
     enabled: true
     config:
       index_name: "supplement-therapy"
       index_directory: "./faiss_index"
       chunk_size: 1000
       chunk_overlap: 200
   ```

### Workflow Configuration

Workflows are defined in `resources/structure.yaml`:

```yaml
workflows:
  - name: "Supplement Therapy"
    description: "Personalized supplement recommendations"
    prompt: |
      Based on the blood test results and health assessment,
      provide evidence-based supplement recommendations...
```

### Troubleshooting

#### Common Issues

1. **FAISS Index Not Found**
   - Ensure INDEX_NAME in environment matches structure.yaml
   - Run `python scripts/init_rag.py` to create index

2. **Connection Issues with Claude Desktop**
   - Verify server is running: check /health endpoint
   - Ensure configuration JSON is valid
   - Restart Claude Desktop completely

3. **Docker Build Failures**
   - Check Python version compatibility
   - Ensure all files are included in build context
   - Verify FAISS index exists in Docker image

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

### Acknowledgments

- Medical reference values based on work by Dr. Ulrich Strunz and Dr. Helena Orfanos-Boeckel
- Built with FastMCP, FastAPI, and LangChain
- Deployed on Railway cloud platform