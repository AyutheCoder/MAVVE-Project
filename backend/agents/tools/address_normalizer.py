"""
Address Normalizer Tool.
Parses unstructured address text into a structured format and scores completeness.
"""

from typing import Dict, Any, Optional
from langchain_core.tools import tool
import structlog
import re

logger = structlog.get_logger()

def _extract_pincode(text: str) -> Optional[str]:
    """Extract a 6-digit Indian pincode from text."""
    match = re.search(r'\b\d{6}\b', text)
    return match.group(0) if match else None

def _calculate_completeness(structured: Dict[str, Any]) -> float:
    """Calculate an address confidence score between 0.0 and 1.0."""
    score = 0.0
    
    if structured.get("street_or_area"):
        score += 0.3
    if structured.get("landmark"):
        score += 0.3
    if structured.get("house_number"):
        score += 0.2
    if structured.get("district_or_city"):
        score += 0.1
    if structured.get("pincode"):
        score += 0.1
        
    return min(score, 1.0)


@tool
def address_normalizer(raw_text: str) -> Dict[str, Any]:
    """
    Parse an unstructured, raw address string into structured components.
    It returns the structured components and a confidence score indicating completeness.
    
    Args:
        raw_text (str): The raw text provided by the user describing their address.
        
    Returns:
        Dict containing structured fields (house_number, street_or_area, landmark, 
        district_or_city, state, pincode) and a 'confidence_score' float (0.0-1.0).
    """
    logger.info("address_normalizer_called", text_length=len(raw_text))
    
    text_lower = raw_text.lower()
    
    # Very rudimentary parsing logic for simulation
    # In production, this would use a dedicated NLP model or Google Maps Geocoding API
    
    structured: Dict[str, Any] = {
        "house_number": None,
        "street_or_area": None,
        "landmark": None,
        "district_or_city": None,
        "state": None,
        "pincode": _extract_pincode(raw_text)
    }
    
    # Try to find landmarks (e.g. "near X", "behind Y", "opposite Z")
    landmark_match = re.search(r'(near|behind|opposite|opp|paas|samne|peeche)\s+([a-z\s]+)(?:,|$)', text_lower)
    if landmark_match:
        structured["landmark"] = landmark_match.group(2).strip().title()
        
    # Try to find district (e.g., "dist X", "district Y")
    dist_match = re.search(r'dist(?:rict)?\.?\s+([a-z\s]+)(?:,|$)', text_lower)
    if dist_match:
        structured["district_or_city"] = dist_match.group(1).strip().title()
        
    # Heuristics for other fields
    if len(raw_text) > 15:
        structured["street_or_area"] = raw_text[:20].strip() # Mock extraction
        
    confidence = _calculate_completeness(structured)
    
    return {
        "structured_address": structured,
        "confidence_score": confidence
    }
