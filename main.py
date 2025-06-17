"""
Main entry point for the Blood Test Reference Values API.
"""
import uvicorn
from bloodtest_tools.api import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug"
    )
