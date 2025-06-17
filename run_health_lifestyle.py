#!/usr/bin/env python3
"""
Health & Lifestyle Workflow MCP Server

This script starts an MCP server with the Health & Lifestyle workflow configuration.
"""
import os
import logging
from pathlib import Path
from server import BookMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    # Define possible config file locations
    config_paths = [
        Path("books/health_lifestyle_workflow.yaml"),
        Path("resources/health_lifestyle_workflow.yaml"),
        Path("app/books/health_lifestyle_workflow.yaml"),
        Path("app/resources/health_lifestyle_workflow.yaml"),
        Path("/app/books/health_lifestyle_workflow.yaml"),
        Path("/app/resources/health_lifestyle_workflow.yaml"),
    ]
    
    # Use the first config file that exists, or the first one as default
    config_path = next((p for p in config_paths if p.exists()), config_paths[0])
    logger.info(f"Using config file: {config_path.absolute()}")

    # Initialize and start the MCP server
    mcp = BookMCPServer(config_path=config_path)
    
    # Get host and port from environment variables or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting Health & Lifestyle MCP server on {host}:{port}")
    mcp.run(host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
