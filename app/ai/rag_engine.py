"""RAG engine orchestrating retrieval and generation."""
import logging
from typing import List, Dict, Optional
from app.ai.llm import LLM
from app.ai.prompts import get_system_prompt
from app.database.vector_db import VectorDatabase

logger = logging.getLogger(__name__)

class RAGEngine:
    """Orchestrates knowledge base retrieval and LLM response generation."""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.llm = LLM()
    
    async def get_response(
        self,
        query: str,
        language: str = "hi",
        context: Optional[List[Dict]] = None,
        caller_id: str = None
    ) -> str:
        """Execute RAG pipeline to generate answers."""
        try:
            intent = await self.llm.classify_intent(query)
            
            # Semantic search with intent-based filtering
            docs = await self.vector_db.search(
                query=query,
                top_k=3,
                filter_metadata={"category": intent} if intent != "general" else None
            )
            
            context_text = self._format_context(docs)
            system_prompt = get_system_prompt(language=language, context=intent)
            
            return await self.llm.generate_response(
                query=query,
                context=context_text,
                system_prompt=system_prompt,
                history=context
            )
            
        except Exception as e:
            logger.error(f"RAG Error: {e}", exc_info=True)
            fallbacks = {
                "hi": "क्षमा करें, समस्या हो रही है। कृपया 1800-233-1332 पर कॉल करें।",
                "en": "Sorry, I'm having trouble. Please contact 1800-233-1332.",
                "chhattisgarhi": "माफ करना, परेशानी हो रहे हे। सरकारी दफ्तर ले संपर्क करव।"
            }
            return fallbacks.get(language, fallbacks["hi"])
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Convert retrieved snippets into a single context string."""
        if not documents:
            return "No relevant information found."
        
        return "\n".join([
            f"[Source {i+1}]: {doc.get('content')}" 
            for i, doc in enumerate(documents)
        ])
