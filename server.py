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

# Configuration de base pour un livre
class BookConfig(BaseModel):
    title: str
    author: str
    domain: str  # Ex: "strategy", "marketing", "leadership"
    description: str
    version: str = "1.0"
    
class ConceptConfig(BaseModel):
    name: str
    description: str
    prerequisites: List[str] = []
    related_concepts: List[str] = []

class MethodConfig(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    concepts_used: List[str]
    prompt_template: str
    examples: List[Dict[str, Any]] = []

class BookKnowledgeConfig(BaseModel):
    book: BookConfig
    concepts: List[ConceptConfig]
    methods: List[MethodConfig]
    custom_instructions: str = ""

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
        self._setup_tools()
        self._setup_prompts()
    
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
        """Automatically configures tools based on the book's methods"""
        self.logger.debug("Setting up dynamic tools for book methods.")
        for method in self.config.methods:
            self._create_dynamic_tool(method)
        self.logger.debug("Setting up generic tools.")
        self._setup_generic_tools()
        self.logger.info("All tools set up successfully.")
    
    def _create_dynamic_tool(self, method: MethodConfig):
        """Dynamically creates an MCP tool for each book method"""
        self.logger.debug(f"Creating dynamic tool for method: {method.name}")
        input_model = self._create_input_model(method)
        
        async def dynamic_method(request: input_model) -> str:
            self.logger.info(f"Executing method: {method.name} with input: {request.dict()}")
            return await self._execute_method(method, request.dict())
        
        # Configuration du décorateur
        dynamic_method.__name__ = method.name.lower().replace(' ', '_')
        dynamic_method.__doc__ = method.description
        
        # Enregistrement de l'outil
        self.mcp.tool()(dynamic_method)
        self.logger.debug(f"Tool registered: {dynamic_method.__name__}")
    
    def _create_input_model(self, method: MethodConfig):
        """Creates a dynamic Pydantic model based on the method's schema"""
        self.logger.debug(f"Creating input model for method: {method.name}")
        fields = {}
        for field_name, field_info in method.input_schema.items():
            if isinstance(field_info, dict):
                description = field_info.get('description', '')
                fields[field_name] = (str, Field(description=description))
            else:
                fields[field_name] = (str, Field())
        
        model = type(f"{method.name}Request", (BaseModel,), {
            "__annotations__": {k: v[0] for k, v in fields.items()},
            **{k: v[1] for k, v in fields.items()}
        })
        self.logger.debug(f"Input model created: {model.__name__}")
        return model
    
    async def _execute_method(self, method: MethodConfig, inputs: Dict[str, Any]) -> str:
        """Returns the final prompt for a book method with the provided inputs"""
        self.logger.info(f"Building context and prompt for method: {method.name}")
        try:
            context = self._build_context(method, inputs)
            final_prompt = self._build_prompt(method, context, inputs)
            self.logger.debug(f"Prompt built for method {method.name}.")
            return final_prompt
        except Exception as e:
            self.logger.error(f"Error executing method {method.name}: {e}")
            raise
    
    def _build_context(self, method: MethodConfig, inputs: Dict[str, Any]) -> str:
        """Builds the context with the book's concepts"""
        self.logger.debug(f"Building context for method: {method.name}")
        context_parts = []
        
        # Informations sur le livre
        context_parts.append(f"BOOK: {self.config.book.title} by {self.config.book.author}")
        context_parts.append(f"DOMAIN: {self.config.book.domain}")
        
        # Concepts utilisés par cette méthode
        relevant_concepts = [c for c in self.config.concepts if c.name in method.concepts_used]
        if relevant_concepts:
            context_parts.append("\nKEY CONCEPTS:")
            for concept in relevant_concepts:
                context_parts.append(f"- {concept.name}: {concept.description}")
        
        # Instructions personnalisées
        if self.config.custom_instructions:
            context_parts.append(f"\nSPECIFIC INSTRUCTIONS:\n{self.config.custom_instructions}")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, method: MethodConfig, context: str, inputs: Dict[str, Any]) -> str:
        """Builds the final prompt by combining context, template, and inputs"""
        self.logger.debug(f"Building prompt for method: {method.name}")
        # Remplacement des variables dans le template
        formatted_template = method.prompt_template
        for key, value in inputs.items():
            formatted_template = formatted_template.replace(f"{{{key}}}", str(value))
        
        final_prompt = f"""
{context}

METHOD TO APPLY: {method.name}
{method.description}

{formatted_template}

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
                "available_methods": [m.name for m in self.config.methods],
                "concepts": [c.name for c in self.config.concepts]
            }
        
        @self.mcp.tool()
        async def list_methods() -> List[Dict[str, Any]]:
            """Lists all available methods of the book"""
            self.logger.info("list_methods called.")
            return [
                {
                    "name": m.name,
                    "description": m.description,
                    "concepts_used": m.concepts_used,
                    "input_fields": list(m.input_schema.keys())
                }
                for m in self.config.methods
            ]
        
        @self.mcp.tool()
        async def explain_concept(concept_name: str) -> str:
            """Explains a specific concept from the book"""
            self.logger.info(f"explain_concept called for: {concept_name}")
            concept = next((c for c in self.config.concepts if c.name.lower() == concept_name.lower()), None)
            if not concept:
                self.logger.warning(f"Concept not found: {concept_name}")
                return f"Concept '{concept_name}' not found."
            
            explanation = f"**{concept.name}**\n\n{concept.description}"
            
            if concept.prerequisites:
                explanation += f"\n\n**Prerequisites:** {', '.join(concept.prerequisites)}"
            
            if concept.related_concepts:
                explanation += f"\n\n**Related concepts:** {', '.join(concept.related_concepts)}"
            
            return explanation
    
    def _setup_prompts(self):
        """Configures system prompts (override if necessary)"""
        self.logger.debug("Setting up system prompts.")
        pass
    
    # @abstractmethod
    # async def _call_llm(self, prompt: str) -> str:
    #     """LLM call - must be implemented by subclasses"""
    #     pass
    
    def run(self, **kwargs):
        """Starts the MCP server"""
        self.logger.info(f"Starting MCP server with args: {kwargs}")
        self.mcp.run(**kwargs)

# =======================
# UTILISATION
# =======================

if __name__ == "__main__":

    config_path = Path("books/gtd.yaml")

    mcp = BookMCPServer(config_path=config_path)
    
    if os.environ.get("ENV") == "DEV":
        mcp.run(host="127.0.0.1", port=8000, transport="sse")
    else:
        mcp.run(host="0.0.0.0", port=8000, transport="sse")