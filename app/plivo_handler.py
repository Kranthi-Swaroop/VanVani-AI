"""Plivo voice call handler for VanVani AI."""
import logging
from typing import Dict, Optional
from plivo import plivoxml
from app.config import get_settings
from app.ai.rag_engine import RAGEngine
from app.utils.language import detect_language
from app.database.sql_db import save_conversation, get_caller_history

logger = logging.getLogger(__name__)
settings = get_settings()


class PlivoVoiceHandler:
    """Handle Plivo voice calls with AI-powered responses."""
    
    def __init__(self):
        """Initialize Plivo voice handler."""
        self.rag_engine = RAGEngine()
        self.active_calls: Dict[str, Dict] = {}
        logger.info("PlivoVoiceHandler initialized")
    
    def handle_incoming_call(self, call_uuid: str, from_number: str) -> str:
        """
        Handle incoming Plivo call.
        
        Args:
            call_uuid: Plivo call UUID
            from_number: Caller's phone number
            
        Returns:
            Plivo XML response
        """
        try:
            logger.info(f"Incoming Plivo call from {from_number}, UUID: {call_uuid}")
            
            # Initialize call session
            self.active_calls[call_uuid] = {
                'from': from_number,
                'language': 'hi',  # Default to Hindi
                'conversation_history': []
            }
            
            # Create Plivo XML response
            response = plivoxml.ResponseElement()
            
            # Welcome message in Hindi
            speak = plivoxml.SpeakElement(
                "नमस्ते! VanVani AI में आपका स्वागत है। आप किसी भी सरकारी योजना, स्वास्थ्य, कृषि या अन्य जानकारी के बारे में पूछ सकते हैं।",
                voice='Polly.Aditi',
                language='hi-IN'
            )
            response.add(speak)
            
            # Get speech input
            get_input = plivoxml.GetInputElement(
                action=f'{settings.host or "http://localhost:8000"}/plivo/process-speech',
                method='POST',
                input_type='speech',
                speech_model='default',
                speech_language='hi-IN',
                timeout=5,
                speech_end_timeout=2
            )
            
            # Prompt for question
            prompt_speak = plivoxml.SpeakElement(
                "कृपया अपना सवाल पूछें।",
                voice='Polly.Aditi',
                language='hi-IN'
            )
            get_input.add(prompt_speak)
            response.add(get_input)
            
            # If no input, hangup gracefully
            hangup = plivoxml.HangupElement()
            response.add(hangup)
            
            return response.to_string()
            
        except Exception as e:
            logger.error(f"Error handling incoming Plivo call: {str(e)}", exc_info=True)
            
            # Error response
            response = plivoxml.ResponseElement()
            error_speak = plivoxml.SpeakElement(
                "क्षमा करें, कुछ गलत हो गया। कृपया फिर से कोशिश करें।",
                voice='Polly.Aditi',
                language='hi-IN'
            )
            response.add(error_speak)
            hangup = plivoxml.HangupElement()
            response.add(hangup)
            
            return response.to_string()
    
    async def handle_speech_input(
        self,
        call_uuid: str,
        speech_input: str,
        speech_language: Optional[str] = None
    ) -> str:
        """
        Process speech input and generate AI response.
        
        Args:
            call_uuid: Plivo call UUID
            speech_input: Transcribed speech text
            speech_language: Detected language code
            
        Returns:
            Plivo XML response with AI answer
        """
        try:
            logger.info(f"Processing speech for call {call_uuid}: {speech_input}")
            
            # Get call session
            call_data = self.active_calls.get(call_uuid, {})
            
            # Detect language
            detected_lang = detect_language(speech_input)
            call_data['language'] = detected_lang
            
            # Get AI response
            ai_response = await self.rag_engine.get_response(
                query=speech_input,
                language=detected_lang,
                conversation_history=call_data.get('conversation_history', [])
            )
            
            # Update conversation history
            if 'conversation_history' not in call_data:
                call_data['conversation_history'] = []
            
            call_data['conversation_history'].append({
                'role': 'user',
                'content': speech_input
            })
            call_data['conversation_history'].append({
                'role': 'assistant',
                'content': ai_response
            })
            
            self.active_calls[call_uuid] = call_data
            
            # Save conversation to database
            await save_conversation(
                caller_id=call_data.get('from', ''),
                call_sid=call_uuid,
                user_query=speech_input,
                ai_response=ai_response,
                language=detected_lang
            )
            
            # Create Plivo XML response
            response = plivoxml.ResponseElement()
            
            # Speak AI response
            voice_map = {
                'hi': 'Polly.Aditi',
                'en': 'Polly.Raveena',
                'chhattisgarhi': 'Polly.Aditi',
                'gondi': 'Polly.Aditi',
                'halbi': 'Polly.Aditi'
            }
            
            lang_map = {
                'hi': 'hi-IN',
                'en': 'en-IN',
                'chhattisgarhi': 'hi-IN',
                'gondi': 'hi-IN',
                'halbi': 'hi-IN'
            }
            
            speak = plivoxml.SpeakElement(
                ai_response,
                voice=voice_map.get(detected_lang, 'Polly.Aditi'),
                language=lang_map.get(detected_lang, 'hi-IN')
            )
            response.add(speak)
            
            # Ask if they have another question
            get_input = plivoxml.GetInputElement(
                action=f'{settings.host or "http://localhost:8000"}/plivo/process-speech',
                method='POST',
                input_type='speech',
                speech_model='default',
                speech_language=lang_map.get(detected_lang, 'hi-IN'),
                timeout=5,
                speech_end_timeout=2
            )
            
            follow_up = plivoxml.SpeakElement(
                "क्या आपका कोई और सवाल है?" if detected_lang == 'hi' else "Do you have another question?",
                voice=voice_map.get(detected_lang, 'Polly.Aditi'),
                language=lang_map.get(detected_lang, 'hi-IN')
            )
            get_input.add(follow_up)
            response.add(get_input)
            
            # Thank you and hangup if no more input
            thank_you = plivoxml.SpeakElement(
                "धन्यवाद! VanVani AI का उपयोग करने के लिए आपका धन्यवाद।",
                voice='Polly.Aditi',
                language='hi-IN'
            )
            response.add(thank_you)
            
            hangup = plivoxml.HangupElement()
            response.add(hangup)
            
            return response.to_string()
            
        except Exception as e:
            logger.error(f"Error processing speech input: {str(e)}", exc_info=True)
            
            # Error response
            response = plivoxml.ResponseElement()
            error_speak = plivoxml.SpeakElement(
                "क्षमा करें, मुझे जवाब देने में समस्या हो रही है। कृपया फिर से कोशिश करें।",
                voice='Polly.Aditi',
                language='hi-IN'
            )
            response.add(error_speak)
            hangup = plivoxml.HangupElement()
            response.add(hangup)
            
            return response.to_string()
    
    def handle_call_status(self, call_uuid: str, status: str):
        """
        Handle call status updates.
        
        Args:
            call_uuid: Plivo call UUID
            status: Call status (completed, failed, etc.)
        """
        try:
            logger.info(f"Call {call_uuid} status: {status}")
            
            # Clean up call session
            if call_uuid in self.active_calls:
                del self.active_calls[call_uuid]
            
        except Exception as e:
            logger.error(f"Error handling call status: {str(e)}")
