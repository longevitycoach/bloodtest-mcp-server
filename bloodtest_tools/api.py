"""
FastAPI application for the Blood Test Reference Values API.
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

from .reference_values import (
    get_reference_range,
    list_available_parameters,
    Sex
)

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

class SexQuery(str, Enum):
    MALE = "male"
    FEMALE = "female"

class ReferenceRangeResponse(BaseModel):
    parameter: str
    unit: str
    optimal_range: str
    classical_range: str
    explanation: str
    sex_specific: bool
    sex_specific_range: Optional[str] = None

class ParameterListResponse(BaseModel):
    parameters: List[Dict[str, str]]

@app.get("/parameters", response_model=ParameterListResponse, summary="List all available parameters")
async def list_parameters():
    """
    Get a list of all available blood test parameters with their units.
    """
    return {"parameters": list_available_parameters()}

@app.get("/reference/{parameter}", response_model=ReferenceRangeResponse, summary="Get reference range for a parameter")
async def get_reference(
    parameter: str,
    sex: Optional[SexQuery] = Query(None, description="Optional sex for sex-specific ranges")
):
    """
    Get the reference range for a specific blood test parameter.
    
    Args:
        parameter: The blood test parameter to look up (case-insensitive).
        sex: Optional sex of the patient for sex-specific ranges.
    """
    try:
        sex_enum = Sex[sex.upper()] if sex else None
        return get_reference_range(parameter, sex_enum)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Blood Test Reference Values API",
        "version": "1.0.0",
        "description": "API for retrieving optimal blood test reference values based on medical guidelines.",
        "endpoints": {
            "GET /parameters": "List all available parameters",
            "GET /reference/{parameter}": "Get reference range for a specific parameter"
        }
    }

