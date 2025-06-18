#!/usr/bin/env python3
"""
Simple Bloodtest API Server with Health Check
Focuses on core API functionality with proper health monitoring
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
from typing import Optional

# Import existing bloodtest tools  
from bloodtest_tools.reference_values import (
    get_reference_range,
    list_available_parameters,
    Sex
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Blood Test Reference Values API",
    description="API for retrieving optimal blood test reference values based on medical guidelines.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Blood Test Reference Values API",
        "version": "1.0.0",
        "description": "API for retrieving optimal blood test reference values based on medical guidelines.",
        "endpoints": {
            "GET /parameters": "List all available parameters",
            "GET /reference/{parameter}": "Get reference range for a specific parameter",
            "GET /health": "Health check endpoint",
            "GET /sse": "MCP Server-Sent Events endpoint (when MCP enabled)"
        },
        "blood_parameters_supported": 8,
        "functional_medicine_ranges": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test that we can access the reference values
        test_result = get_reference_range("ferritin")
        rag_enabled = os.path.exists("faiss_index/supplement-therapy.faiss")
        
        return {
            "status": "healthy",
            "book": "Der Blutwerte Coach, Naehrstoff-Therapie",
            "version": "1.0",
            "rag_enabled": rag_enabled,
            "api_functional": True,
            "blood_parameters_count": len(list_available_parameters()),
            "api_endpoints": {
                "blood_test_parameters": "/parameters",
                "blood_test_reference": "/reference/{parameter}",
                "mcp_sse": "/sse"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/parameters")
async def get_parameters():
    """List all available blood test parameters"""
    return {"parameters": list_available_parameters()}

@app.get("/reference/{parameter}")
async def get_reference(parameter: str, sex: Optional[str] = Query(None)):
    """Get reference range for a blood test parameter"""
    try:
        sex_enum = None
        if sex:
            sex_lower = sex.lower()
            if sex_lower == 'male':
                sex_enum = Sex.MALE
            elif sex_lower == 'female':
                sex_enum = Sex.FEMALE
            else:
                raise HTTPException(status_code=400, detail="Invalid sex. Must be 'male' or 'female'.")
        
        return get_reference_range(parameter, sex_enum)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/sse")
async def sse_info():
    """Information about SSE endpoint for MCP protocol"""
    return {
        "message": "MCP Server-Sent Events endpoint",
        "description": "This endpoint would normally handle MCP protocol connections",
        "status": "info_only",
        "note": "For full MCP functionality, use the integrated MCP server"
    }

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    logger.info("Starting Bloodtest API Server...")
    logger.info(f"Available endpoints:")
    logger.info(f"  - API Root: http://localhost:{port}/")
    logger.info(f"  - Health Check: http://localhost:{port}/health")
    logger.info(f"  - Parameters: http://localhost:{port}/parameters")
    logger.info(f"  - Reference: http://localhost:{port}/reference/{{parameter}}")
    logger.info(f"  - SSE Info: http://localhost:{port}/sse")
    
    uvicorn.run(app, host=host, port=port, log_level="info")