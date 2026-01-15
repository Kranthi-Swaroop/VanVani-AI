"""Vector database for storing and retrieving knowledge base documents."""
import os
import logging
from typing import List, Dict, Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available, using simple fallback")
    from app.database.simple_vector_db import SimpleVectorDatabase

class VectorDatabase:
    """Manages persistent vector storage for semantic search."""
    
    def __init__(self):
        try:
            if not CHROMADB_AVAILABLE:
                self.simple_db = SimpleVectorDatabase()
                self.using_simple = True
                return
            
            self.using_simple = False
            os.makedirs(settings.vector_db_path, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=settings.vector_db_path,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
            )
            self.collection = self.client.get_or_create_collection(
                name="vanvani_knowledge",
                metadata={"description": "VanVani AI knowledge base"}
            )
        except Exception as e:
            logger.error(f"VectorDB Init Error: {e}")
            raise

    async def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        try:
            if self.using_simple:
                await self.simple_db.add_documents(documents, metadatas, ids)
            else:
                self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    async def search(self, query: str, top_k: int = 3, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        try:
            if self.using_simple:
                results = await self.simple_db.search(query, n_results=top_k)
                return [{"content": r['document'], "metadata": r['metadata']} for r in results]
            
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_metadata or None
            )
            
            docs = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    docs.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                    })
            return docs
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    def count_documents(self) -> int:
        return self.simple_db.count_documents() if self.using_simple else self.collection.count()

    def delete_all(self):
        if self.using_simple:
            self.simple_db.reset()
        else:
            self.client.delete_collection("vanvani_knowledge")
            self.collection = self.client.create_collection("vanvani_knowledge")

async def reload_vector_db():
    try:
        from app.database.load_data import load_all_documents
        db = VectorDatabase()
        db.delete_all()
        await load_all_documents(db)
        logger.info("Vector database reloaded successfully")
    except Exception as e:
        logger.error(f"Reload Error: {e}")
        raise
