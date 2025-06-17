"""
MCP tool for retrieving optimal blood test reference values.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from fastapi import HTTPException

from .reference_values import (
    get_reference_range,
    list_available_parameters,
    Sex
)

class BloodTestTool:
    """MCP tool for retrieving optimal blood test reference values."""
    
    @staticmethod
    def get_optimal_values(parameter: str, sex: Optional[str] = None) -> Dict[str, Any]:
        """
        Get optimal reference values for a specific blood test parameter.
        
        Args:
            parameter: The blood test parameter to look up (case-insensitive).
            sex: Optional sex of the patient ('male' or 'female') for sex-specific ranges.
            
        Returns:
            Dictionary containing reference range information.
            
        Raises:
            HTTPException: If the parameter is not found or invalid sex is provided.
        """
        try:
            # Convert sex string to enum if provided
            sex_enum = None
            if sex:
                sex_lower = sex.lower()
                if sex_lower == 'male':
                    sex_enum = Sex.MALE
                elif sex_lower == 'female':
                    sex_enum = Sex.FEMALE
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid sex. Must be 'male' or 'female'."
                    )
            
            return get_reference_range(parameter, sex_enum)
            
        except ValueError as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )
    
    @staticmethod
    def list_parameters() -> List[Dict[str, str]]:
        """
        Get a list of all available blood test parameters with their units.
        
        Returns:
            List of dictionaries containing parameter names and units.
        """
        return list_available_parameters()


# Pydantic models for API documentation and validation
class BloodTestParameterRequest(BaseModel):
    parameter: str = Field(
        ...,
        description="The blood test parameter to look up (case-insensitive)",
        example="vitamin d"
    )
    sex: Optional[str] = Field(
        None,
        description="Optional sex of the patient for sex-specific ranges ('male' or 'female')",
        example="female"
    )

class BloodTestParameterResponse(BaseModel):
    parameter: str = Field(..., description="The requested blood test parameter")
    unit: str = Field(..., description="The unit of measurement for the parameter")
    optimal_range: str = Field(..., description="Optimal reference range")
    classical_range: str = Field(..., description="Classical reference range")
    explanation: str = Field(..., description="Explanation of the parameter and its significance")
    sex_specific: bool = Field(..., description="Whether the parameter has sex-specific ranges")
    sex_specific_range: Optional[str] = Field(
        None,
        description="Specific range for the provided sex (if applicable and available)"
    )

class BloodTestParameterListResponse(BaseModel):
    parameters: List[Dict[str, str]] = Field(
        ...,
        description="List of available blood test parameters with their units"
    )

# Create an instance of the tool to be used by the MCP server
blood_test_tool = BloodTestTool()
