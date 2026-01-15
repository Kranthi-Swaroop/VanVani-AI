"""Simple in-memory vector database fallback (no ChromaDB dependency)."""
import logging
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class SimpleVectorDatabase:
    """Simple in-memory vector database using basic text search."""
    
    def __init__(self, persist_path: str = "./simple_vector_db.json"):
        """Initialize simple vector database."""
        self.persist_path = persist_path
        self.documents = []
        self.metadatas = []
        self.ids = []
        
        # Load existing data if available
        self._load()
        
        logger.info(f"Simple vector database initialized with {len(self.documents)} documents")
    
    def _load(self):
        """Load database from disk."""
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.metadatas = data.get('metadatas', [])
                    self.ids = data.get('ids', [])
            except Exception as e:
                logger.warning(f"Could not load database: {e}")
    
    def _save(self):
        """Save database to disk."""
        try:
            data = {
                'documents': self.documents,
                'metadatas': self.metadatas,
                'ids': self.ids
            }
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Could not save database: {e}")
    
    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ):
        """Add documents to the database."""
        for doc_id, doc, metadata in zip(ids, documents, metadatas):
            # Update if exists, add if new
            if doc_id in self.ids:
                idx = self.ids.index(doc_id)
                self.documents[idx] = doc
                self.metadatas[idx] = metadata
            else:
                self.ids.append(doc_id)
                self.documents.append(doc)
                self.metadatas.append(metadata)
        
        self._save()
        logger.info(f"Added {len(documents)} documents")
    
    async def search(
        self,
        query: str,
        n_results: int = 3,
        language: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for relevant documents.
        Simple keyword-based search (not semantic).
        """
        # Convert query to lowercase for matching
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each document
        scored_results = []
        for i, (doc, metadata) in enumerate(zip(self.documents, self.metadatas)):
            # Skip if language filter doesn't match
            if language and metadata.get('language') != language:
                continue
            
            doc_lower = doc.lower()
            doc_words = set(doc_lower.split())
            
            # Calculate simple word overlap score
            overlap = len(query_words.intersection(doc_words))
            
            # Bonus for exact phrase match
            if query_lower in doc_lower:
                overlap += 10
            
            if overlap > 0:
                scored_results.append({
                    'score': overlap,
                    'document': doc,
                    'metadata': metadata,
                    'id': self.ids[i]
                })
        
        # Sort by score and return top N
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        results = scored_results[:n_results]
        
        logger.debug(f"Search for '{query}' returned {len(results)} results")
        return results
    
    def count_documents(self) -> int:
        """Return the number of documents."""
        return len(self.documents)
    
    def reset(self):
        """Clear all documents."""
        self.documents = []
        self.metadatas = []
        self.ids = []
        self._save()
        logger.info("Database reset")
