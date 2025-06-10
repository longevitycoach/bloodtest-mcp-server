# =======================
# FRAMEWORK DE BASE
# =======================

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import json
import yaml
from pathlib import Path
import logging

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
        self.config = self._load_config(config_path)
        self.mcp = FastMCP(f"{self.config.book.title} - Activation MCP")
        self._setup_tools()
        self._setup_prompts()
    
    def _load_config(self, config_path: Path) -> BookKnowledgeConfig:
        """Charge la configuration du livre depuis YAML/JSON"""
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        return BookKnowledgeConfig(**data)
    
    def _setup_tools(self):
        """Configure automatiquement les outils basés sur les méthodes du livre"""
        for method in self.config.methods:
            self._create_dynamic_tool(method)
        
        # Outils génériques
        self._setup_generic_tools()
    
    def _create_dynamic_tool(self, method: MethodConfig):
        """Crée dynamiquement un outil MCP pour chaque méthode du livre"""
        
        # Création du modèle Pydantic dynamique pour la validation
        input_model = self._create_input_model(method)
        
        async def dynamic_method(request: input_model) -> str:
            return await self._execute_method(method, request.dict())
        
        # Configuration du décorateur
        dynamic_method.__name__ = method.name.lower().replace(' ', '_')
        dynamic_method.__doc__ = method.description
        
        # Enregistrement de l'outil
        self.mcp.tool()(dynamic_method)
    
    def _create_input_model(self, method: MethodConfig):
        """Crée un modèle Pydantic dynamique basé sur le schéma de la méthode"""
        fields = {}
        for field_name, field_info in method.input_schema.items():
            if isinstance(field_info, dict):
                description = field_info.get('description', '')
                fields[field_name] = (str, Field(description=description))
            else:
                fields[field_name] = (str, Field())
        
        return type(f"{method.name}Request", (BaseModel,), {
            "__annotations__": {k: v[0] for k, v in fields.items()},
            **{k: v[1] for k, v in fields.items()}
        })
    
    async def _execute_method(self, method: MethodConfig, inputs: Dict[str, Any]) -> str:
        """Retourne le prompt final pour une méthode du livre avec les inputs fournis"""
        # Construction du contexte
        context = self._build_context(method, inputs)
        
        # Construction du prompt final
        final_prompt = self._build_prompt(method, context, inputs)

        return final_prompt
    
    def _build_context(self, method: MethodConfig, inputs: Dict[str, Any]) -> str:
        """Construit le contexte avec les concepts du livre"""
        context_parts = []
        
        # Informations sur le livre
        context_parts.append(f"LIVRE: {self.config.book.title} par {self.config.book.author}")
        context_parts.append(f"DOMAINE: {self.config.book.domain}")
        
        # Concepts utilisés par cette méthode
        relevant_concepts = [c for c in self.config.concepts if c.name in method.concepts_used]
        if relevant_concepts:
            context_parts.append("\nCONCEPTS CLÉS:")
            for concept in relevant_concepts:
                context_parts.append(f"- {concept.name}: {concept.description}")
        
        # Instructions personnalisées
        if self.config.custom_instructions:
            context_parts.append(f"\nINSTRUCTIONS SPÉCIFIQUES:\n{self.config.custom_instructions}")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, method: MethodConfig, context: str, inputs: Dict[str, Any]) -> str:
        """Construit le prompt final en combinant contexte, template et inputs"""
        # Remplacement des variables dans le template
        formatted_template = method.prompt_template
        for key, value in inputs.items():
            formatted_template = formatted_template.replace(f"{{{key}}}", str(value))
        
        final_prompt = f"""
{context}

MÉTHODE À APPLIQUER: {method.name}
{method.description}

{formatted_template}

Applique rigoureusement la méthodologie du livre en utilisant les informations fournies.
"""
        return final_prompt
    
    def _setup_generic_tools(self):
        """Configure les outils génériques disponibles pour tous les livres"""
        
        @self.mcp.tool()
        async def get_book_info() -> Dict[str, Any]:
            """Retourne les informations sur le livre activé"""
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
            """Liste toutes les méthodes disponibles du livre"""
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
            """Explique un concept spécifique du livre"""
            concept = next((c for c in self.config.concepts if c.name.lower() == concept_name.lower()), None)
            if not concept:
                return f"Concept '{concept_name}' non trouvé."
            
            explanation = f"**{concept.name}**\n\n{concept.description}"
            
            if concept.prerequisites:
                explanation += f"\n\n**Prérequis:** {', '.join(concept.prerequisites)}"
            
            if concept.related_concepts:
                explanation += f"\n\n**Concepts liés:** {', '.join(concept.related_concepts)}"
            
            return explanation
    
    def _setup_prompts(self):
        """Configure les prompts système (à override si nécessaire)"""
        pass
    
    # @abstractmethod
    # async def _call_llm(self, prompt: str) -> str:
    #     """Appel au LLM - doit être implémenté par les classes filles"""
    #     pass
    
    def run(self, **kwargs):
        """Lance le serveur MCP"""
        self.mcp.run(**kwargs)

# =======================
# UTILISATION
# =======================

if __name__ == "__main__":

    config_path = Path("gtd.yaml")

    mcp = BookMCPServer(config_path=config_path)
    mcp.run(host="127.0.0.1", port=8000, transport="sse")
    