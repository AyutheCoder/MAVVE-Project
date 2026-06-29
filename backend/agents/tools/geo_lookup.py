"""
Geo Lookup Tool.
Provides mock geographic database with landmarks for Indian pincodes.
"""

from typing import List, Dict, Any
from langchain_core.tools import tool
import structlog

logger = structlog.get_logger()

# ── Mock Geographic Database ─────────────────────────────
# Simulates a geo-database that maps pincodes to known local landmarks
MOCK_GEO_DB = {
    # Nashik, Maharashtra
    "422001": [
        {"name": "Kalaram Temple", "type": "temple", "distance_category": "central"},
        {"name": "Panchavati", "type": "area", "distance_category": "central"},
        {"name": "Nashik Road Railway Station", "type": "transit", "distance_category": "outskirts"},
        {"name": "CBS Bus Stand", "type": "transit", "distance_category": "central"},
    ],
    # Rural Nashik Example
    "422207": [
        {"name": "Ozar Airport", "type": "airport", "distance_category": "nearby"},
        {"name": "HAL Township", "type": "area", "distance_category": "central"},
        {"name": "Saptashrungi Temple", "type": "temple", "distance_category": "far"},
    ],
    # Rural UP (Lucknow outskirts)
    "226010": [
        {"name": "Gomti Nagar Railway Station", "type": "transit", "distance_category": "nearby"},
        {"name": "Bhootnath Market", "type": "market", "distance_category": "central"},
        {"name": "Hanuman Mandir", "type": "temple", "distance_category": "central"},
    ],
    # Rural Bihar (Patna outskirts)
    "800013": [
        {"name": "Danapur Station", "type": "transit", "distance_category": "central"},
        {"name": "Sanjay Gandhi Jaivik Udyan", "type": "park", "distance_category": "far"},
        {"name": "Patna High Court", "type": "government", "distance_category": "far"},
    ],
    # Add a generic fallback for other pincodes
    "default": [
        {"name": "Main Post Office", "type": "government", "distance_category": "central"},
        {"name": "Gram Panchayat Bhawan", "type": "government", "distance_category": "central"},
        {"name": "Shiv Temple", "type": "temple", "distance_category": "nearby"},
        {"name": "Government School", "type": "education", "distance_category": "central"},
        {"name": "Primary Health Centre", "type": "health", "distance_category": "nearby"},
        {"name": "Bus Stand", "type": "transit", "distance_category": "central"},
    ]
}


@tool
def geo_lookup(pincode: str) -> List[Dict[str, Any]]:
    """
    Search for known landmarks near a given pincode.
    Use this to help a user identify their exact location when their address is vague.
    
    Args:
        pincode (str): The 6-digit Indian postal code.
        
    Returns:
        List of dictionaries containing 'name', 'type', and 'distance_category' of landmarks.
    """
    logger.info("geo_lookup_called", pincode=pincode)
    
    # Strip spaces just in case
    clean_pincode = str(pincode).strip()
    
    if clean_pincode in MOCK_GEO_DB:
        landmarks = MOCK_GEO_DB[clean_pincode]
    else:
        # For testing, we return generic rural landmarks if not found
        landmarks = MOCK_GEO_DB["default"]
        
    return landmarks
