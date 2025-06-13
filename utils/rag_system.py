# =======================
# RAG SYSTEM MODULE - FAISS VERSION
# =======================

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import hashlib
import json
import pickle

logger = logging.getLogger(__name__)

class RAGSystem:
    """Système RAG pour indexer et rechercher dans des documents PDF avec FAISS"""
    
    def __init__(
        self,
        index_name: str = "book_knowledge",
        index_directory: str = "./faiss_index",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialise le système RAG avec FAISS
        
        Args:
            index_name: Nom de l'index FAISS
            index_directory: Répertoire pour sauvegarder l'index
            embedding_model: Modèle d'embedding à utiliser
            chunk_size: Taille des chunks en caractères
            chunk_overlap: Chevauchement entre chunks
        """
        self.index_name = index_name
        self.index_directory = Path(index_directory)
        self.index_directory.mkdir(exist_ok=True)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Chemins des fichiers
        self.index_path = self.index_directory / f"{index_name}.faiss"
        self.metadata_path = self.index_directory / f"{index_name}_metadata.pkl"
        self.hash_path = self.index_directory / f"{index_name}_hashes.json"
        
        # Configuration de l'embedding
        logger.info(f"Initializing embeddings with model: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Charger ou initialiser le vector store
        self.vector_store = self._load_or_create_vector_store()
        
        # Charger les hashes des documents indexés
        self.indexed_hashes = self._load_indexed_hashes()
    
    def _load_or_create_vector_store(self) -> Optional[FAISS]:
        """Charge un index FAISS existant ou retourne None"""
        if self.index_path.exists():
            try:
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                vector_store = FAISS.load_local(
                    str(self.index_directory),
                    self.embeddings,
                    index_name=self.index_name,
                    allow_dangerous_deserialization=True  # Nécessaire pour charger les metadatas
                )
                logger.info("FAISS index loaded successfully")
                return vector_store
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                return None
        else:
            logger.info("No existing FAISS index found")
            return None
    
    def _save_vector_store(self):
        """Sauvegarde l'index FAISS"""
        if self.vector_store:
            logger.info(f"Saving FAISS index to {self.index_path}")
            self.vector_store.save_local(
                str(self.index_directory),
                index_name=self.index_name
            )
            logger.info("FAISS index saved successfully")
    
    def _load_indexed_hashes(self) -> Dict[str, str]:
        """Charge les hashes des documents déjà indexés"""
        if self.hash_path.exists():
            try:
                with open(self.hash_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load hashes: {e}")
        return {}
    
    def _save_indexed_hashes(self):
        """Sauvegarde les hashes des documents indexés"""
        with open(self.hash_path, 'w') as f:
            json.dump(self.indexed_hashes, f)
    
    def _get_document_hash(self, file_path: str) -> str:
        """Calcule le hash MD5 d'un fichier"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _is_document_indexed(self, file_path: str) -> bool:
        """Vérifie si un document est déjà indexé"""
        doc_hash = self._get_document_hash(file_path)
        return file_path in self.indexed_hashes and self.indexed_hashes[file_path] == doc_hash
    
    def index_pdf(self, pdf_path: str, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Indexe un fichier PDF dans le vector store FAISS
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            force_reindex: Force la réindexation même si le document existe
            
        Returns:
            Dict avec les statistiques d'indexation
        """
        logger.info(f"Starting PDF indexing: {pdf_path}")
        
        # Vérifier si le document est déjà indexé
        if not force_reindex and self._is_document_indexed(pdf_path):
            logger.info(f"Document already indexed: {pdf_path}")
            return {
                "status": "already_indexed",
                "pdf_path": pdf_path,
                "chunks_added": 0
            }
        
        try:
            # 1. Charger le PDF
            logger.info("Loading PDF...")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from PDF")
            
            # 2. Découper en chunks
            logger.info("Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")
            
            # 3. Ajouter des métadonnées
            doc_hash = self._get_document_hash(pdf_path)
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "source": pdf_path,
                    "document_hash": doc_hash,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "book_title": Path(pdf_path).stem
                })
            
            # 4. Créer ou mettre à jour le vector store
            if self.vector_store is None or force_reindex:
                # Créer un nouveau vector store
                logger.info("Creating new FAISS index...")
                self.vector_store = FAISS.from_documents(
                    chunks,
                    self.embeddings
                )
            else:
                # Ajouter au vector store existant
                logger.info("Adding chunks to existing FAISS index...")
                self.vector_store.add_documents(chunks)
            
            # 5. Sauvegarder l'index et les métadonnées
            self._save_vector_store()
            
            # 6. Mettre à jour les hashes
            self.indexed_hashes[pdf_path] = doc_hash
            self._save_indexed_hashes()
            
            logger.info(f"Successfully indexed {len(chunks)} chunks")
            
            return {
                "status": "success",
                "pdf_path": pdf_path,
                "chunks_added": len(chunks),
                "document_hash": doc_hash
            }
            
        except Exception as e:
            logger.error(f"Failed to index PDF: {e}")
            return {
                "status": "error",
                "pdf_path": pdf_path,
                "error": str(e)
            }
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche dans le vector store FAISS
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats à retourner
            filter_metadata: Filtres sur les métadonnées (non supporté par FAISS de base)
            
        Returns:
            Liste des chunks pertinents avec leurs scores
        """
        logger.info(f"Searching for: {query}")
        
        if self.vector_store is None:
            logger.warning("No vector store available")
            return []
        
        try:
            # Recherche par similarité
            results = self.vector_store.similarity_search_with_score(
                query,
                k=k
            )
            
            # Formater et filtrer les résultats si nécessaire
            formatted_results = []
            for doc, score in results:
                # Appliquer les filtres manuellement si spécifiés
                if filter_metadata:
                    match = all(
                        doc.metadata.get(key) == value 
                        for key, value in filter_metadata.items()
                    )
                    if not match:
                        continue
                
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur l'index FAISS"""
        try:
            stats = {
                "index_name": self.index_name,
                "index_exists": self.index_path.exists(),
                "indexed_documents": len(self.indexed_hashes),
                "documents": list(self.indexed_hashes.keys())
            }
            
            if self.vector_store:
                # Obtenir le nombre de vecteurs dans l'index
                try:
                    stats["total_vectors"] = self.vector_store.index.ntotal
                except:
                    stats["total_vectors"] = "unknown"
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {
                "error": str(e)
            }


def setup_rag_tool(mcp, rag_system: RAGSystem):
    """Configure l'outil RAG pour FastMCP"""
    
    @mcp.tool()
    async def search_book_knowledge(
        query: str,
        max_results: int = 5,
        book_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search through the book's content using semantic search.
        
        Args:
            query: Your search query
            max_results: Maximum number of results to return (default: 5)
            book_title: Filter by specific book title (optional)
        
        Returns:
            Relevant chunks from the book with similarity scores
        """
        logger.info(f"RAG search requested: {query}")
        
        # Préparer les filtres
        filter_metadata = None
        if book_title:
            filter_metadata = {"book_title": book_title}
        
        # Effectuer la recherche
        results = rag_system.search(
            query=query,
            k=max_results,
            filter_metadata=filter_metadata
        )
        
        return {
            "query": query,
            "results_count": len(results),
            "results": results
        }
    
    @mcp.tool()
    async def get_rag_stats() -> Dict[str, Any]:
        """Get statistics about the RAG knowledge base"""
        return rag_system.get_index_stats()