"""Language detection and processing utilities."""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Pattern matching for basic language detection
LANGUAGE_PATTERNS = {
    "hi": ["है", "हैं", "का", "की", "के", "में", "से", "को", "ने", "पर"],
    "chhattisgarhi": ["हे", "हवय", "हावय", "के", "म", "ले", "बर", "मोर", "तोर"],
    "gondi": ["ఆనా", "ఆమా", "నీ", "మీ", "ఉంది"], # Tribal patterns
    "halbi": ["मोक", "तोक", "हवे", "नइ", "करना", "होना"],
    "en": ["is", "are", "the", "of", "in", "to", "and", "for", "what", "how"]
}

LANGUAGE_CODE_MAP = {
    "hi": "hi-IN",
    "chhattisgarhi": "hi-IN",
    "gondi": "hi-IN",
    "halbi": "hi-IN",
    "en": "en-IN"
}

def detect_language(text: str) -> str:
    """Detect language of input text based on keyword density."""
    if not text: return "hi"
    
    t = text.lower()
    scores = {lang: sum(1 for p in pats if p in t) for lang, pats in LANGUAGE_PATTERNS.items()}
    detected = max(scores, key=scores.get)
    return detected if scores[detected] > 0 else "hi"

def get_language_code(language: str) -> str:
    return LANGUAGE_CODE_MAP.get(language, "hi-IN")

def get_greeting(language: str = "hi") -> str:
    greetings = {
        "hi": "नमस्कार! मैं वनवाणी हूं। मैं आपकी कैसे मदद कर सकती हूं?",
        "chhattisgarhi": "नमस्कार! मैं वनवाणी हवं। मैं तोर कइसे मदद कर सकत हवं?",
        "en": "Hello! I am VanVani. How can I help you?",
        "gondi": "सेवा सेवा! नन्ना वनवाणी। नन्ना नीवा मदद बर्ता कीकन?",
        "halbi": "नमस्कार! मैं वनवाणी हवे। मोक तोर कैसे मदद करना हे?"
    }
    return greetings.get(language, greetings["hi"])
