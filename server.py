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
        self.logger.debug(f"Loading configuration from {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            self.logger.info("Configuration loaded successfully.")
            return BookKnowledgeConfig(**data)
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
    
    def run(self, **kwargs):
        """Starts the MCP server"""
        self.logger.info(f"Starting MCP server with args: {kwargs}")
        self.mcp.run(**kwargs)

# =======================
# UTILISATION
# =======================

if __name__ == "__main__":

    config_path = Path("books/structure.yaml")

    mcp = BookMCPServer(config_path=config_path)
    
    if os.environ.get("ENV") == "DEV":
        mcp.run(host="127.0.0.1", port=8000, transport="sse")
    else:
        mcp.run(host="0.0.0.0", port=8000, transport="sse")