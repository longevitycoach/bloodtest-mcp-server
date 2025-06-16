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
    pdf_directory = os.getenv("PDF_DIRECTORY", "scripts/pdfs")
    index_name = os.getenv("INDEX_NAME", "book_knowledge")
    index_directory = os.getenv("INDEX_DIRECTORY", "faiss_index")
    force_reindex = os.getenv("FORCE_REINDEX", "false").lower() == "true"
    
    logger.info("=== RAG Initialization Script (FAISS) ===")
    logger.info(f"PDF Directory: {pdf_directory}")
    logger.info(f"Index Name: {index_name}")
    logger.info(f"Index Directory: {index_directory}")
    logger.info(f"Force Reindex: {force_reindex}")
    
    # Trouver les PDFs dans le répertoire
    pdf_dir_path = Path(pdf_directory)
    if not pdf_dir_path.is_dir():
        logger.error(f"PDF directory not found: {pdf_dir_path}")
        sys.exit(1)
        
    pdf_files = list(pdf_dir_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_dir_path}")

    logger.info(f"Found {len(pdf_files)} PDF(s) to index in '{pdf_directory}'.")

    try:
        # Initialiser le système RAG
        rag_system = RAGSystem(
            index_name=index_name,
            index_directory=index_directory,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        total_chunks_added = 0
        
        # Indexer chaque PDF
        for pdf_path in pdf_files:
            logger.info(f"--- Indexing {pdf_path.name} ---")
            result = rag_system.index_pdf(
                pdf_path=str(pdf_path),
                force_reindex=force_reindex
            )
            
            if result["status"] == "success":
                chunks = result.get('chunks_added', 0)
                total_chunks_added += chunks
                logger.info(f"✅ Successfully indexed {chunks} chunks from {pdf_path.name}")
            elif result["status"] == "already_indexed":
                logger.info(f"✅ {pdf_path.name} already indexed, skipping...")
            else:
                logger.error(f"❌ Indexation failed for {pdf_path.name}: {result.get('error', 'Unknown error')}")
        
        logger.info(f"--- Total new chunks added: {total_chunks_added} ---")

        # Afficher les stats finales
        stats = rag_system.get_index_stats()
        logger.info(f"Final index stats: {stats}")
        
        logger.info("=== RAG initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()