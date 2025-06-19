#!/usr/bin/env python3
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
        # Convert config path to absolute Path object
        config_path = Path("books/health_lifestyle_workflow.yaml").resolve()
        logger.info(f"Starting server with config: {config_path}")
        
        # Verify the config file exists
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        # Initialize and start the server with SSE transport
        mcp = BookMCPServer(config_path=config_path)
        # Using SSE transport for HTTP/SSE communication on port 8001
        mcp.run(transport="sse", host="0.0.0.0", port=8001)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
