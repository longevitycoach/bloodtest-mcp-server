#!/usr/bin/env python3
"""
Railway-optimized server entry point with proper health checks
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
    try:
        # Try multiple possible locations for the config file
        possible_config_paths = [
            Path("resources/structure.yaml"),
            Path("books/structure.yaml"),
            Path("app/resources/structure.yaml"),
            Path("/app/resources/structure.yaml")
        ]
        
        # Use the first config file that exists
        config_path = None
        for path in possible_config_paths:
            if path.exists():
                config_path = path
                break
        
        if not config_path:
            # Fallback to health_lifestyle_workflow.yaml if structure.yaml not found
            fallback_paths = [
                Path("books/health_lifestyle_workflow.yaml"),
                Path("/app/books/health_lifestyle_workflow.yaml")
            ]
            for path in fallback_paths:
                if path.exists():
                    config_path = path
                    break
        
        if not config_path:
            raise FileNotFoundError("No configuration file found")
            
        logger.info(f"Starting server with config: {config_path}")
        
        # Initialize and start the server with SSE transport
        mcp = BookMCPServer(config_path=config_path)
        
        # Get port from environment variable or default to 8000
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Run with SSE transport - this properly sets up the health endpoint
        mcp.run(transport="sse", host=host, port=port)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()