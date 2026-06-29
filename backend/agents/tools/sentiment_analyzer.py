"""
Sentiment Analyzer Tool.
Classifies user responses into specific categories for Intent Verification.
"""

from typing import Dict, Any, Literal
from langchain_core.tools import tool
import structlog
import re

logger = structlog.get_logger()

def _classify_sentiment(text: str) -> Literal["confident", "hesitant", "evasive", "hostile"]:
    """Simple heuristic-based classification for the demo/MVP."""
    text_lower = text.lower()
    
    # 1. Hostile / Cancellation intent
    if any(word in text_lower for word in ["cancel", "no", "don't want", "nahi", "cancel kar", "wapas", "fraud", "scam", "wrong", "fake"]):
        return "hostile"
        
    # 2. Hesitant / Arranging money / Minor ordered
    if any(word in text_lower for word in ["wait", "maybe", "arrange", "son ordered", "bacche ne", "galti", "mistake", "kal", "tomorrow", "paisa", "ruko"]):
        return "hesitant"
        
    # 3. Evasive
    if any(word in text_lower for word in ["who", "kaun", "why", "kya", "later", "baad me"]):
        return "evasive"
        
    # 4. Confident / Confirmed
    if any(word in text_lower for word in ["yes", "haan", "ho", "send", "bhej", "deliver", "ready", "confirm"]):
        return "confident"
        
    # Default fallback
    return "hesitant"

@tool
def analyze_intent_sentiment(raw_response: str) -> Dict[str, Any]:
    """
    Analyze the customer's response to determine their intent confidence.
    
    Args:
        raw_response (str): The raw text response from the customer.
        
    Returns:
        Dict containing 'classification' (confident, hesitant, evasive, hostile).
    """
    logger.info("analyze_intent_sentiment_called", text_length=len(raw_response))
    
    classification = _classify_sentiment(raw_response)
    
    return {
        "classification": classification,
        "is_high_risk": classification in ["evasive", "hostile"],
        "requires_reassurance": classification == "hesitant"
    }
