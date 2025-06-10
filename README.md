# Book MCP Server

This project is a generic MCP server for activating and running book-based methods and concepts. It is designed to load a book configuration (YAML) and expose methods and concepts as MCP API tools.

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
