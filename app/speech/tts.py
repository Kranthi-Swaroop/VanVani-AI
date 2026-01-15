"""Text-to-Speech module for natural voice synthesis."""
import logging
from typing import Optional
import os
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TextToSpeech:
    """Handle text-to-speech conversion in multiple languages."""
    
    def __init__(self):
        """Initialize TTS services."""
        self.sarvam_available = bool(settings.sarvam_api_key)
        self.google_available = bool(settings.google_application_credentials)
        
        if self.google_available:
            from google.cloud import texttospeech
            self.google_client = texttospeech.TextToSpeechClient()
        
        logger.info(f"TTS initialized - Sarvam: {self.sarvam_available}, Google: {self.google_available}")
    
    async def synthesize_speech(
        self, 
        text: str, 
        language_code: str = "hi-IN",
        gender: str = "FEMALE"
    ) -> Optional[bytes]:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert
            language_code: Language code (e.g., 'hi-IN')
            gender: Voice gender ('MALE' or 'FEMALE')
            
        Returns:
            Audio data in bytes or None if failed
        """

        if self.sarvam_available:
            result = await self._synthesize_sarvam(text, language_code, gender)
            if result:
                return result
        
        # Fallback to Google Cloud TTS
        if self.google_available:
            result = await self._synthesize_google(text, language_code, gender)
            if result:
                return result
        
        logger.error("No TTS service available or all failed")
        return None
    
    async def _synthesize_sarvam(
        self, 
        text: str, 
        language_code: str,
        gender: str
    ) -> Optional[bytes]:
        """Synthesize speech using Sarvam.ai."""
        try:
            import httpx
            
            # Map language codes
            lang_map = {
                "hi-IN": "hi",
                "en-IN": "en",
                "ta-IN": "ta",
                "te-IN": "te",
                "mr-IN": "mr",
                "bn-IN": "bn",
            }
            
            sarvam_lang = lang_map.get(language_code, "hi")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sarvam.ai/text-to-speech",
                    headers={
                        "Authorization": f"Bearer {settings.sarvam_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "language": sarvam_lang,
                        "speaker": gender.lower(),
                        "pitch": 0,
                        "pace": 1.0,
                        "loudness": 1.0
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    audio_data = response.content
                    logger.info(f"Sarvam TTS successful: {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.error(f"Sarvam TTS error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Sarvam TTS error: {str(e)}")
            return None
    
    async def _synthesize_google(
        self, 
        text: str, 
        language_code: str,
        gender: str
    ) -> Optional[bytes]:
        """Synthesize speech using Google Cloud Text-to-Speech."""
        try:
            from google.cloud import texttospeech
            
            # Set the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Select voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, gender, texttospeech.SsmlVoiceGender.FEMALE)
            )
            
            # Select audio config
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Perform TTS
            response = self.google_client.synthesize_speech(
                input=synthesis_input, 
                voice=voice, 
                audio_config=audio_config
            )
            
            logger.info(f"Google TTS successful: {len(response.audio_content)} bytes")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Google TTS error: {str(e)}")
            return None
    
    def get_available_voices(self, language_code: str = None) -> list:
        """Get list of available voices."""
        if not self.google_available:
            return []
        
        try:
            from google.cloud import texttospeech
            
            voices = self.google_client.list_voices(language_code=language_code)
            
            return [
                {
                    "name": voice.name,
                    "language_codes": voice.language_codes,
                    "gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name
                }
                for voice in voices.voices
            ]
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return []
