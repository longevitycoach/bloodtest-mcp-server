"""
Main entry point for the Blood Test Reference Values API.
"""
import os
import logging
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Configure application monitoring
def configure_monitoring():
    """Initialize application monitoring (Sentry removed)."""
    logger.info("Application monitoring is disabled (Sentry removed)")

# Initialize monitoring
configure_monitoring()

# Import the FastAPI app
from bloodtest_tools.api import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default 8000
    port = int(os.getenv("PORT", 8000))
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "bloodtest_tools.api:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        workers=1 if os.getenv("ENV") == "development" else None
    )
