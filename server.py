# =======================
# BASE FRAMEWORK
# =======================

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import json
import yaml
from pathlib import Path
import logging
import os

# Import the sequential thinking tool
from utils.sequential_thinking import setup_sequential_thinking_tool
# Import RAG system
from utils.rag_system import RAGSystem, setup_rag_tool

# Configuration de base pour un livre
class BookConfig(BaseModel):
    title: str
    author: str
    domain: str  # Ex: "strategy", "marketing", "leadership"
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

# =======================
# CLASSE DE BASE ABSTRAITE
# =======================

class BookMCPServer(ABC):
    def __init__(self, config_path: Path):
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(
            level=logging.DEBUG if os.environ.get("ENV") == "DEV" else logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger.info(f"Initializing BookMCPServer with config: {config_path}")
        self.config = self._load_config(config_path)
        self.mcp = FastMCP(f"{self.config.book.title} - Activation MCP")
        
        # Initialize RAG system if enabled
        self.rag_system = None
        if self.config.tools.get("rag", ToolConfig()).enabled:
            self._init_rag_system()
        
        self._setup_tools()
        self._setup_prompts()
    
    def _init_rag_system(self):
        """Initialize RAG system with FAISS"""
        self.logger.info("Initializing RAG system...")
        
        rag_config = self.config.tools.get("rag", ToolConfig()).config
        
        # Get configuration from environment or config
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
            self.logger.info("RAG system initialized successfully with FAISS")
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            self.logger.warning("RAG functionality will be disabled")
            self.rag_system = None
    
    def _load_config(self, config_path: Path) -> BookKnowledgeConfig:
        """Loads the book configuration from YAML/JSON"""
        self.logger.debug(f"Attempting to load configuration from {config_path}")
        
        # List of possible locations to try for the config file
        possible_locations = [
            config_path,  # Original path
            Path("resources") / config_path.name,  # New resources directory
            Path("app") / config_path,  # Docker container path
            Path("/app") / config_path,  # Absolute Docker container path
            Path("/app/resources") / config_path.name  # Resources in Docker
        ]
        
        config_data = None
        actual_path = None
        
        # Try each possible location
        for path in possible_locations:
            try:
                self.logger.debug(f"Trying to load config from: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    if path.suffix == '.yaml' or path.suffix == '.yml':
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                actual_path = path
                self.logger.info(f"Configuration loaded successfully from: {path}")
                break
            except FileNotFoundError:
                continue
            except Exception as e:
                self.logger.warning(f"Error loading config from {path}: {e}")
                continue
        
        if config_data is None:
            raise FileNotFoundError(
                f"Could not find configuration file in any of these locations: {', '.join(str(p) for p in possible_locations)}"
            )
            
        try:
            return BookKnowledgeConfig(**config_data)
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _setup_tools(self):
        """Automatically configures tools based on the book's workflows and enabled tools"""
        self.logger.debug("Setting up dynamic tools for book workflows.")
        for workflow in self.config.workflows:
            self._create_workflow_tool(workflow)
        
        self.logger.debug("Setting up generic tools.")
        self._setup_generic_tools()
        
        # Setup configured tools
        self.logger.debug("Setting up configured tools.")
        self._setup_configured_tools()
        
        self.logger.info("All tools set up successfully.")
    
    def _create_workflow_tool(self, workflow: WorkflowConfig):
        """Creates an MCP tool for each workflow"""
        self.logger.debug(f"Creating tool for workflow: {workflow.name}")
        
        async def workflow_method() -> str:
            self.logger.info(f"Executing workflow: {workflow.name}")
            return await self._execute_workflow(workflow)
        
        # Configuration du décorateur
        workflow_method.__name__ = workflow.name.lower().replace(' ', '_')
        workflow_method.__doc__ = workflow.description
        
        # Enregistrement de l'outil
        self.mcp.tool()(workflow_method)
        self.logger.debug(f"Tool registered: {workflow_method.__name__}")
    
    async def _execute_workflow(self, workflow: WorkflowConfig) -> str:
        """Returns the final prompt for a workflow"""
        self.logger.info(f"Building context and prompt for workflow: {workflow.name}")
        try:
            context = self._build_context(workflow)
            final_prompt = self._build_prompt(workflow, context)
            self.logger.debug(f"Prompt built for workflow {workflow.name}.")
            return final_prompt
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow.name}: {e}")
            raise
    
    def _build_context(self, workflow: WorkflowConfig) -> str:
        """Builds the context with the book's information"""
        self.logger.debug(f"Building context for workflow: {workflow.name}")
        context_parts = []
        
        # Informations sur le livre
        context_parts.append(f"BOOK: {self.config.book.title} by {self.config.book.author}")
        context_parts.append(f"DOMAIN: {self.config.book.domain}")
        
        # Instructions personnalisées
        if self.config.custom_instructions:
            context_parts.append(f"\nSPECIFIC INSTRUCTIONS:\n{self.config.custom_instructions}")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, workflow: WorkflowConfig, context: str) -> str:
        """Builds the final prompt by combining context and workflow prompt"""
        self.logger.debug(f"Building prompt for workflow: {workflow.name}")
        
        final_prompt = f"""
{context}

WORKFLOW TO APPLY: {workflow.name}
{workflow.description}

{workflow.prompt}

Strictly apply the book's methodology using the information provided.
"""
        return final_prompt
    
    def _setup_generic_tools(self):
        """Configures generic tools available for all books"""
        self.logger.debug("Registering generic tools.")
        @self.mcp.tool()
        async def get_book_info() -> Dict[str, Any]:
            """Returns information about the activated book"""
            self.logger.info("get_book_info called.")
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
            self.logger.info("list_workflows called.")
            return [
                {
                    "name": w.name,
                    "description": w.description
                }
                for w in self.config.workflows
            ]
    
    def _setup_configured_tools(self):
        """Setup tools based on configuration"""
        self.logger.debug("Setting up configured tools.")
        
        # Setup sequential thinking if enabled
        if self.config.tools.get("sequential_thinking", ToolConfig()).enabled:
            self.logger.debug("Setting up sequential thinking tool.")
            try:
                setup_sequential_thinking_tool(self.mcp)
                self.logger.info("Sequential thinking tool setup successfully.")
            except Exception as e:
                self.logger.error(f"Failed to setup sequential thinking tool: {e}")
                raise
        
        # Setup RAG tool if enabled and initialized
        if self.rag_system:
            self.logger.debug("Setting up RAG tool.")
            try:
                setup_rag_tool(self.mcp, self.rag_system)
                self.logger.info("RAG tool setup successfully.")
            except Exception as e:
                self.logger.error(f"Failed to setup RAG tool: {e}")
                raise
    
    def _setup_prompts(self):
        """Configures system prompts (override if necessary)"""
        self.logger.debug("Setting up system prompts.")
        pass
    
    def _setup_health_check(self):
        """Configures the health check endpoint"""
        from starlette.responses import JSONResponse
        from starlette.routing import Route
        
        async def health_check(request):
            """Health check endpoint for monitoring"""
            return JSONResponse({
                "status": "healthy",
                "book": self.config.book.title,
                "version": self.config.book.version,
                "rag_enabled": bool(self.rag_system)
            })
        
        # Create a route for the health check
        health_route = Route("/health", health_check, methods=["GET"])
        
        # Add the route to the FastMCP server's HTTP app
        if not hasattr(self.mcp, '_additional_http_routes'):
            self.mcp._additional_http_routes = []
        self.mcp._additional_http_routes.append(health_route)
        
        self.logger.info("Health check endpoint configured at /health")
    
    def run(self, **kwargs):
        """Starts the MCP server"""
        self.logger.info(f"Starting MCP server with args: {kwargs}")
        self._setup_health_check()
        self.mcp.run(**kwargs)

# =======================
# UTILISATION
# =======================

if __name__ == "__main__":
    # Try multiple possible locations for the config file
    possible_config_paths = [
        Path("resources/structure.yaml"),  # New location in resources directory
        Path("books/structure.yaml"),     # Old location for backward compatibility
        Path("app/resources/structure.yaml"),  # Common Docker path
        Path("/app/resources/structure.yaml")  # Absolute Docker path
    ]
    
    # Use the first config file that exists, or the first one as default
    config_path = next((p for p in possible_config_paths if p.exists()), possible_config_paths[0])
    print(f"Using config file: {config_path.absolute()}")

    mcp = BookMCPServer(config_path=config_path)
    
    # Get host and port from environment variables or use defaults
    # Always use 0.0.0.0 in container to allow external connections
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on {host}:{port}")
    mcp.run(host=host, port=port, transport="sse")