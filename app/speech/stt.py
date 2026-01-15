"""Speech-to-Text module supporting multiple Indian languages."""
import logging
from typing import Optional
import os
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SpeechToText:
    """Handle speech-to-text conversion for multiple Indian languages."""
    
    def __init__(self):
        """Initialize STT services."""
        self.sarvam_available = bool(settings.sarvam_api_key)
        self.google_available = bool(settings.google_application_credentials)
        
        if self.google_available:
            from google.cloud import speech
            self.google_client = speech.SpeechClient()
        
        logger.info(f"STT initialized - Sarvam: {self.sarvam_available}, Google: {self.google_available}")
    
    async def transcribe_audio(
        self, 
        audio_data: bytes, 
        language_hint: str = "hi-IN"
    ) -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio data in bytes
            language_hint: Language code hint (e.g., 'hi-IN', 'en-IN')
            
        Returns:
            Transcribed text or None if failed
        """

        if self.sarvam_available:
            result = await self._transcribe_sarvam(audio_data, language_hint)
            if result:
                return result
        
        # Fallback to Google Cloud Speech
        if self.google_available:
            result = await self._transcribe_google(audio_data, language_hint)
            if result:
                return result
        
        logger.error("No STT service available or all failed")
        return None
    
    async def _transcribe_sarvam(
        self, 
        audio_data: bytes, 
        language_hint: str
    ) -> Optional[str]:
        """Transcribe using Sarvam.ai API."""
        try:
            import httpx
            
            # Map language codes to Sarvam.ai format
            lang_map = {
                "hi-IN": "hi",
                "en-IN": "en",
            }
            
            sarvam_lang = lang_map.get(language_hint, "hi")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sarvam.ai/speech-to-text",
                    headers={
                        "Authorization": f"Bearer {settings.sarvam_api_key}",
                        "Content-Type": "application/octet-stream"
                    },
                    params={"language": sarvam_lang},
                    content=audio_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    transcript = result.get("transcript", "")
                    logger.info(f"Sarvam transcription: {transcript}")
                    return transcript
                else:
                    logger.error(f"Sarvam API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Sarvam transcription error: {str(e)}")
            return None
    
    async def _transcribe_google(
        self, 
        audio_data: bytes, 
        language_hint: str
    ) -> Optional[str]:
        """Transcribe using Google Cloud Speech-to-Text."""
        try:
            from google.cloud import speech
            
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=8000,  # Phone call quality
                language_code=language_hint,
                alternative_language_codes=["hi-IN", "en-IN"],
                enable_automatic_punctuation=True,
                model="phone_call"
            )
            
            # Perform transcription
            response = self.google_client.recognize(config=config, audio=audio)
            
            # Extract transcript
            for result in response.results:
                transcript = result.alternatives[0].transcript
                logger.info(f"Google transcription: {transcript}")
                return transcript
            
            return None
            
        except Exception as e:
            logger.error(f"Google transcription error: {str(e)}")
            return None
    
    def get_supported_languages(self) -> list:
        """Get list of supported language codes."""
        return [
            "hi-IN",  # Hindi
            "en-IN",  # English (India)
            "ta-IN",  # Tamil
            "te-IN",  # Telugu
            "mr-IN",  # Marathi
            "bn-IN",  # Bengali
            "gu-IN",  # Gujarati
            "kn-IN",  # Kannada
            "ml-IN",  # Malayalam
            "pa-IN",  # Punjabi
        ]
