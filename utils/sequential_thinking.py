# =======================
# SEQUENTIAL THINKING TOOL
# =======================

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import logging

class ThoughtData(BaseModel):
    thought: str = Field(..., description="Your current thinking step")
    thought_number: int = Field(..., ge=1, description="Current thought number")
    total_thoughts: int = Field(..., ge=1, description="Estimated total thoughts needed")
    next_thought_needed: bool = Field(..., description="Whether another thought step is needed")
    is_revision: Optional[bool] = Field(None, description="Whether this revises previous thinking")
    revises_thought: Optional[int] = Field(None, ge=1, description="Which thought is being reconsidered")
    branch_from_thought: Optional[int] = Field(None, ge=1, description="Branching point thought number")
    branch_id: Optional[str] = Field(None, description="Branch identifier")
    needs_more_thoughts: Optional[bool] = Field(None, description="If more thoughts are needed")

def setup_sequential_thinking_tool(mcp: FastMCP):
    """Setup the sequential thinking tool with FastMCP"""
    
    @mcp.tool()
    async def sequential_thinking(
        thought: str = Field(..., description="Your current thinking step"),
        thought_number: int = Field(..., ge=1, description="Current thought number"),
        total_thoughts: int = Field(..., ge=1, description="Estimated total thoughts needed"),
        next_thought_needed: bool = Field(..., description="Whether another thought step is needed"),
        is_revision: Optional[bool] = Field(None, description="Whether this revises previous thinking"),
        revises_thought: Optional[int] = Field(None, ge=1, description="Which thought is being reconsidered"),
        branch_from_thought: Optional[int] = Field(None, ge=1, description="Branching point thought number"),
        branch_id: Optional[str] = Field(None, description="Branch identifier"),
        needs_more_thoughts: Optional[bool] = Field(None, description="If more thoughts are needed")
    ) -> str:
        """A detailed tool for dynamic and reflective problem-solving through thoughts.
        
        This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
        Each thought can build on, question, or revise previous insights as understanding deepens.

        When to use this tool:
        - Breaking down complex problems into steps
        - Planning and design with room for revision
        - Analysis that might need course correction
        - Problems where the full scope might not be clear initially
        - Problems that require a multi-step solution
        - Tasks that need to maintain context over multiple steps
        - Situations where irrelevant information needs to be filtered out

        Key features:
        - You can adjust total_thoughts up or down as you progress
        - You can question or revise previous thoughts
        - You can add more thoughts even after reaching what seemed like the end
        - You can express uncertainty and explore alternative approaches
        - Not every thought needs to build linearly - you can branch or backtrack
        - Generates a solution hypothesis
        - Verifies the hypothesis based on the Chain of Thought steps
        - Repeats the process until satisfied
        - Provides a correct answer
        """
        
        try:
            thought_data = ThoughtData(
                thought=thought,
                thought_number=thought_number,
                total_thoughts=max(total_thoughts, thought_number),  # Ensure total >= current
                next_thought_needed=next_thought_needed,
                is_revision=is_revision,
                revises_thought=revises_thought,
                branch_from_thought=branch_from_thought,
                branch_id=branch_id,
                needs_more_thoughts=needs_more_thoughts
            )
            
            # Return simple structured response
            result = {
                "thought_number": thought_data.thought_number,
                "total_thoughts": thought_data.total_thoughts,
                "next_thought_needed": thought_data.next_thought_needed,
                "status": "success"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "status": "failed"
            }
            return json.dumps(error_result, indent=2)