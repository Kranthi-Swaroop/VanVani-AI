"""Voice call handling and session management."""
import logging
from typing import Tuple
from app.ai.rag_engine import RAGEngine
from app.utils.language import detect_language, get_language_code
from app.database.sql_db import save_conversation

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Manages voice interactions and conversation state."""
    
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.active_sessions = {}
    
    async def process_query(
        self, 
        user_input: str, 
        caller_id: str,
        call_sid: str,
        language: str = None
    ) -> Tuple[str, str]:
        """Process user input and generate context-aware AI response."""
        try:
            detected_lang = language or detect_language(user_input)
            language_code = get_language_code(detected_lang)
            
            # Retrieve last 3 turns of context
            history = self.active_sessions.get(call_sid, [])
            
            response = await self.rag_engine.get_response(
                query=user_input,
                language=detected_lang,
                context=history,
                caller_id=caller_id
            )
            
            # Update history and save state
            history.append({"user": user_input, "assistant": response})
            self.active_sessions[call_sid] = history[-3:]
            
            await save_conversation(
                caller_id=caller_id,
                call_sid=call_sid,
                user_query=user_input,
                ai_response=response,
                language=detected_lang
            )
            
            return response, language_code
            
        except Exception as e:
            logger.error(f"VoiceHandler error: {e}", exc_info=True)
            error_messages = {
                "hi": "क्षमा करें, मुझे समस्या हो रही है। कृपया फिर से कोशिश करें।",
                "en": "Sorry, I'm having trouble. Please try again.",
                "chhattisgarhi": "माफ करना, मोला परेशानी हो रहे हे। फेर से कोशिश करव।",
            }
            return error_messages.get(detected_lang, error_messages["hi"]), "hi-IN"
    
    def end_session(self, call_sid: str):
        if call_sid in self.active_sessions:
            del self.active_sessions[call_sid]
