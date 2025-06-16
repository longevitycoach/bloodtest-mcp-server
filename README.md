# Personalized Health Coach MCP Server

This project implements a Retrieval-Augmented Generation (RAG) system that acts as a specialized health coach. It leverages a knowledge base of indexed books to provide personalized nutrition and supplement therapy plans based on user-provided health data, such as blood test results.

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

- `PDF_DIRECTORY`: Path to the directory containing your PDF files (e.g., `resources`).
- `INDEX_NAME`: The desired name for your FAISS index (e.g., `supplement-therapy`). This **must** match the `index_name` in `books/structure.yaml`.
- `INDEX_DIRECTORY`: Directory where the FAISS index will be saved (defaults to `faiss_index`).
- `FORCE_REINDEX`: Set to `true` to force re-indexing even if an index with the same name exists (defaults to `false`).

**Example command to run the script:**

```bash
# Ensure your virtual environment is active
# Make sure your PDFs are in the 'resources' directory (or update PDF_DIRECTORY)

sh -c 'source .venv/bin/activate && INDEX_NAME="supplement-therapy" PDF_DIRECTORY="resources" python scripts/init_rag.py
```

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
python server.py
```

The server will start (defaulting to `http://0.0.0.0:8000`), load the FAISS index, and expose the configured MCP tools.

## 2. Docker Setup

Docker can simplify deployment by packaging the application and its dependencies.

### a. Docker Prerequisites

- Docker Engine
- Docker Compose

### b. Configure `docker-compose.yml`

Review and adjust `docker-compose.yml`. Key environment variables for the `app` service that affect RAG initialization:

- `PDF_DIRECTORY`: **Crucial for Docker.** This should point to the path *inside the container* where your PDFs are mounted. For example, if you mount `./resources` to `/app/resources`, set `PDF_DIRECTORY=/app/resources`.
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

## 3. Testing with an MCP Client

A simple Python script, `client_test.py` (located in the project root), can be used to interact with the running MCP server. See the script for an example of how to connect and call a tool.

```bash
# Ensure the server is running (either locally or in Docker)
# If running locally, ensure your virtual environment is active for the client too, or that 'mcp' is globally available.
source .venv/bin/activate # If applicable
python client_test.py
```

## Features

- Dynamic tool generation from book YAML config
- FastMCP-based server
- Easily extensible for any book or methodology
- Dockerized for easy deployment

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

## Quick Start

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

## Development

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
