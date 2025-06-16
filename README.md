# Personalized Health Coach MCP Server

This project implements a Retrieval-Augmented Generation (RAG) system that acts as a specialized health coach. It leverages a knowledge base of indexed books to provide personalized nutrition and supplement therapy plans based on user-provided health data, such as blood test results.

## 1. Setup and Initialization

First, ensure you have the required dependencies installed. Then, you need to create a knowledge base by indexing your source documents (e.g., PDF books).

### a. Install Dependencies

Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

### b. Initialize the RAG

The `scripts/init_rag.py` script will process your PDF files located in the `books/` directory, create embeddings, and store them in a FAISS vector index.

1. Place your PDF books inside the `/books` directory.
2. Run the initialization script:

```bash
python scripts/init_rag.py
```

This will create a `faiss_index` directory containing the indexed knowledge base for your specific books.

## 2. Customizing the AI Behavior (`structure.yaml`)

The behavior of the AI coach is defined in the `books/structure.yaml` file. After initializing the RAG, you must adapt this file to match your specific domain and the content of your indexed books.

This file controls the AI's role, the information it needs, the process it follows, and the constraints it operates under.

### Key Sections to Adapt

- `<ROLE>`: Define the AI's persona. For example, an "expert in nutrition and supplement therapy."
- `<INPUT_NEEDED>`: Specify the data the AI should collect from the user (e.g., blood markers, lifestyle habits, health goals).
- `<PROCESS>`: Outline the step-by-step workflow the AI should follow. This typically includes data assessment, analysis using the indexed knowledge, and plan formulation.
- `<OUTPUT_EXAMPLE>`: Provide a template for the AI's final output, such as a personalized supplement plan.
- `<SPECIFIC_CONSTRAINTS>`: Set mandatory rules for the AI, such as safety disclaimers, citing sources, and avoiding medical diagnoses.
- `<TONE>`: Describe the desired communication style (e.g., empathetic, scientific, supportive).

By carefully editing these sections, you can tailor the AI's behavior to your exact needs, ensuring it leverages your indexed books effectively and safely.

## 3. Running the MCP Server

Once the RAG is initialized and `structure.yaml` is customized, you can start the MCP server. The server will automatically load the existing FAISS index from the `./faiss_index` directory.

Run the following command in your terminal:

```bash
python server.py
```

The server will start, and the RAG-powered health coach will be ready to receive queries and provide personalized guidance based on its configured workflow and knowledge base.

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
