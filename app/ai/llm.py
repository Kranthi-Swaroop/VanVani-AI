"""LLM integration using Google Gemini models."""
import logging
import asyncio
import google.generativeai as genai
from typing import List, Dict, Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class LLM:
    """Interface for generating responses and classifying intent."""
    
    def __init__(self):
        genai.configure(api_key=settings.google_gemini_api_key)
        self.model = genai.GenerativeModel('gemma-3-4b-it')

    async def generate_response(
        self, query: str, context: str, system_prompt: str, history: Optional[List[Dict]] = None
    ) -> str:
        try:
            hist_txt = "\n".join([f"U: {t.get('user')}\nA: {t.get('assistant')}" for t in (history or [])])
            prompt = f"{system_prompt}\n\nHistory:\n{hist_txt}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer concisely in same language:"
            
            resp = await asyncio.to_thread(self.model.generate_content, prompt)
            return resp.text.strip()
        except Exception as e:
            logger.error(f"Gen Error: {e}")
            return "क्षमा करें, समस्या हो रही है।"

    async def classify_intent(self, query: str) -> str:
        try:
            prompt = f"Classify into one: scheme, health, agriculture, market, civic, general.\nQuery: {query}\nCategory:"
            resp = await asyncio.to_thread(self.model.generate_content, prompt)
            intent = resp.text.strip().lower()
            return intent if intent in ['scheme', 'health', 'agriculture', 'market', 'civic'] else 'general'
        except Exception as e:
            logger.error(f"Classify Error: {e}")
            return 'general'
