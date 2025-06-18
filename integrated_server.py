#!/usr/bin/env python3
"""
Integrated Bloodtest MCP Server with API and Health Check
Combines blood test reference API with MCP protocol support
"""

from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import json
import yaml
from pathlib import Path
import logging
import os

# Import existing bloodtest tools
from bloodtest_tools.reference_values import (
    get_reference_range,
    list_available_parameters,
    Sex
)

# Import the sequential thinking tool
from utils.sequential_thinking import setup_sequential_thinking_tool
# Import RAG system
from utils.rag_system import RAGSystem, setup_rag_tool

# Configuration classes (same as before)
class BookConfig(BaseModel):
    title: str
    author: str
    domain: str
    description: str
    version: str = "1.0"

class WorkflowConfig(BaseModel):
    name: str
    description: str
    prompt: str

class ToolConfig(BaseModel):
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)

class BookKnowledgeConfig(BaseModel):
    book: BookConfig
    workflows: List[WorkflowConfig]
    custom_instructions: str = ""
    tools: Dict[str, ToolConfig] = Field(default_factory=dict)

class IntegratedBloodtestServer:
    """Integrated server providing both API and MCP functionality"""
    
    def __init__(self, config_path: Path):
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(
            level=logging.DEBUG if os.environ.get("ENV") == "DEV" else logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        self.logger.info(f"Initializing Integrated Bloodtest Server with config: {config_path}")
        self.config = self._load_config(config_path)
        
        # Initialize FastMCP
        self.mcp = FastMCP(f"{self.config.book.title} - Integrated Server")
        
        # Initialize RAG system if enabled
        self.rag_system = None
        if self.config.tools.get("rag", ToolConfig()).enabled:
            self._init_rag_system()
        
        # Setup MCP tools
        self._setup_mcp_tools()
        
        # Setup API endpoints
        self._setup_api_endpoints()
        
        self.logger.info("Integrated Bloodtest Server initialized successfully")
    
    def _load_config(self, config_path: Path) -> BookKnowledgeConfig:
        """Load configuration from YAML file"""
        possible_locations = [
            config_path,
            Path("resources") / config_path.name,
            Path("app") / config_path,
            Path("/app") / config_path,
            Path("/app/resources") / config_path.name
        ]
        
        for path in possible_locations:
            try:
                self.logger.debug(f"Trying to load config from: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    if path.suffix in ['.yaml', '.yml']:
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                self.logger.info(f"Configuration loaded successfully from: {path}")
                return BookKnowledgeConfig(**config_data)
            except FileNotFoundError:
                continue
            except Exception as e:
                self.logger.warning(f"Error loading config from {path}: {e}")
                continue
        
        raise FileNotFoundError(f"Could not find configuration file in any location")
    
    def _init_rag_system(self):
        """Initialize RAG system with FAISS"""
        self.logger.info("Initializing RAG system...")
        
        rag_config = self.config.tools.get("rag", ToolConfig()).config
        index_name = rag_config.get("index_name", f"{self.config.book.title.lower().replace(' ', '_')}_knowledge")
        index_directory = os.getenv("INDEX_DIRECTORY", rag_config.get("index_directory", "./faiss_index"))
        
        try:
            self.rag_system = RAGSystem(
                index_name=index_name,
                index_directory=index_directory,
                chunk_size=rag_config.get("chunk_size", 1000),
                chunk_overlap=rag_config.get("chunk_overlap", 200),
                embedding_model=rag_config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
            )
            self.logger.info("RAG system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            self.rag_system = None
    
    def _setup_mcp_tools(self):
        """Setup MCP tools"""
        self.logger.info("Setting up MCP tools...")
        
        # Generic tools
        @self.mcp.tool()
        async def get_book_info() -> Dict[str, Any]:
            """Returns information about the activated book"""
            return {
                "title": self.config.book.title,
                "author": self.config.book.author,
                "domain": self.config.book.domain,
                "description": self.config.book.description,
                "available_workflows": [w.name for w in self.config.workflows],
                "rag_enabled": self.rag_system is not None
            }
        
        @self.mcp.tool()
        async def list_workflows() -> List[Dict[str, Any]]:
            """Lists all available workflows of the book"""
            return [
                {
                    "name": w.name,
                    "description": w.description
                }
                for w in self.config.workflows
            ]
        
        # Dynamic workflow tools
        for workflow in self.config.workflows:
            self._create_workflow_tool(workflow)
        
        # Setup additional tools
        if self.config.tools.get("sequential_thinking", ToolConfig()).enabled:
            try:
                setup_sequential_thinking_tool(self.mcp)
                self.logger.info("Sequential thinking tool setup successfully")
            except Exception as e:
                self.logger.error(f"Failed to setup sequential thinking tool: {e}")
        
        if self.rag_system:
            try:
                setup_rag_tool(self.mcp, self.rag_system)
                self.logger.info("RAG tool setup successfully")
            except Exception as e:
                self.logger.error(f"Failed to setup RAG tool: {e}")
    
    def _create_workflow_tool(self, workflow: WorkflowConfig):
        """Create MCP tool for workflow"""
        async def workflow_method() -> str:
            self.logger.info(f"Executing workflow: {workflow.name}")
            return self._build_workflow_prompt(workflow)
        
        workflow_method.__name__ = workflow.name.lower().replace(' ', '_')
        workflow_method.__doc__ = workflow.description
        self.mcp.tool()(workflow_method)
    
    def _build_workflow_prompt(self, workflow: WorkflowConfig) -> str:
        """Build workflow prompt with context"""
        context_parts = [
            f"BOOK: {self.config.book.title} by {self.config.book.author}",
            f"DOMAIN: {self.config.book.domain}"
        ]
        
        if self.config.custom_instructions:
            context_parts.append(f"\nSPECIFIC INSTRUCTIONS:\n{self.config.custom_instructions}")
        
        context = "\n".join(context_parts)
        
        return f"""
{context}

WORKFLOW TO APPLY: {workflow.name}
{workflow.description}

{workflow.prompt}

Strictly apply the book's methodology using the information provided.
"""
    
    def _setup_api_endpoints(self):
        """Setup blood test reference API endpoints as MCP tools"""
        self.logger.info("Setting up API endpoints as MCP tools...")
        
        # Create HTTP endpoints using FastMCP's method
        @self.mcp.get("/")
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
                    "GET /sse": "MCP Server-Sent Events endpoint"
                },
                "mcp_enabled": True,
                "rag_enabled": bool(self.rag_system)
            }
        
        @self.mcp.get("/health")
        async def health_check():
            """Health check endpoint for monitoring"""
            return {
                "status": "healthy",
                "book": self.config.book.title,
                "version": self.config.book.version,
                "rag_enabled": bool(self.rag_system),
                "api_endpoints": {
                    "blood_test_parameters": "/parameters",
                    "blood_test_reference": "/reference/{parameter}",
                    "mcp_sse": "/sse"
                }
            }
        
        @self.mcp.get("/parameters")
        async def get_parameters():
            """List all available blood test parameters"""
            return {"parameters": list_available_parameters()}
        
        @self.mcp.get("/reference/{parameter}")
        async def get_reference(parameter: str, sex: Optional[str] = None):
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
        
        self.logger.info("API endpoints configured successfully")
    
    def run(self, **kwargs):
        """Start the integrated server"""
        self.logger.info(f"Starting integrated server with args: {kwargs}")
        self.mcp.run(**kwargs)

if __name__ == "__main__":
    # Find configuration file
    possible_config_paths = [
        Path("resources/structure.yaml"),
        Path("books/structure.yaml"),
        Path("app/resources/structure.yaml"),
        Path("/app/resources/structure.yaml")
    ]
    
    config_path = next((p for p in possible_config_paths if p.exists()), possible_config_paths[0])
    print(f"Using config file: {config_path.absolute()}")

    server = IntegratedBloodtestServer(config_path=config_path)
    
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting integrated server on {host}:{port}")
    print("Available endpoints:")
    print("  - API: http://localhost:8000/")
    print("  - Health: http://localhost:8000/health") 
    print("  - Parameters: http://localhost:8000/parameters")
    print("  - Reference: http://localhost:8000/reference/{parameter}")
    print("  - MCP SSE: http://localhost:8000/sse")
    
    server.run(host=host, port=port, transport="sse")