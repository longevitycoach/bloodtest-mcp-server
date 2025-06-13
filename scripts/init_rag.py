#!/usr/bin/env python3
"""
Script d'initialisation du système RAG avec FAISS
Lance l'indexation du PDF au démarrage
"""

import os
import sys
import time
import logging
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.rag_system import RAGSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal"""
    
    # Configuration depuis les variables d'environnement
    pdf_path = os.getenv("PDF_PATH", "/app/books/book.pdf")
    index_name = os.getenv("INDEX_NAME", "book_knowledge")
    index_directory = os.getenv("INDEX_DIRECTORY", "/app/faiss_index")
    force_reindex = os.getenv("FORCE_REINDEX", "false").lower() == "true"
    
    logger.info("=== RAG Initialization Script (FAISS) ===")
    logger.info(f"PDF Path: {pdf_path}")
    logger.info(f"Index Name: {index_name}")
    logger.info(f"Index Directory: {index_directory}")
    logger.info(f"Force Reindex: {force_reindex}")
    
    # Vérifier que le PDF existe
    if not Path(pdf_path).exists():
        logger.error(f"PDF not found: {pdf_path}")
        sys.exit(1)
    
    try:
        # Initialiser le système RAG
        rag_system = RAGSystem(
            index_name=index_name,
            index_directory=index_directory,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Indexer le PDF
        logger.info("Starting PDF indexation...")
        result = rag_system.index_pdf(
            pdf_path=pdf_path,
            force_reindex=force_reindex
        )
        
        if result["status"] == "success":
            logger.info(f"✅ Successfully indexed {result['chunks_added']} chunks")
        elif result["status"] == "already_indexed":
            logger.info("✅ Document already indexed, skipping...")
        else:
            logger.error(f"❌ Indexation failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        # Afficher les stats
        stats = rag_system.get_index_stats()
        logger.info(f"Index stats: {stats}")
        
        logger.info("=== RAG initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()