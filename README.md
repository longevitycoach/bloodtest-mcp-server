# Personalized Health Coach MCP Server

This project implements a Retrieval-Augmented Generation (RAG) system that acts as a specialized health coach. It leverages a knowledge base of indexed books to provide personalized nutrition and supplement therapy plans based on user-provided health data, such as blood test results.

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

## Health Check Endpoint

This project implements a Retrieval-Augmented Generation (RAG) system that acts as a specialized health coach. It leverages a knowledge base of indexed books to provide personalized nutrition and supplement therapy plans based on user-provided health data, such as blood test results.

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
   git clone git@github.com:aymerigermain/book-mcp-server.git
   cd book-mcp-server
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
