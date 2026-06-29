"""
Session Manager.
Maps WhatsApp phone numbers to active MAVVE LangGraph sessions.
"""

import structlog
from typing import Dict, Any, Optional
import uuid

logger = structlog.get_logger()

# In-memory session store for MVP. 
# In production, this would be backed by Redis.
_SESSIONS: Dict[str, Dict[str, Any]] = {}

class SessionManager:
    @staticmethod
    def create_session(phone: str, order_id: str, risk_factors: list) -> str:
        """Create a new MAVVE session for a user."""
        session_id = f"mavve_{uuid.uuid4().hex[:8]}"
        
        # Initial MAVVE State
        _SESSIONS[phone] = {
            "session_id": session_id,
            "order_id": order_id,
            "phone": phone,
            "state": {
                "order_id": order_id,
                "user_id": "resolved_from_phone", # Mock
                "user_language": "hi", # Default, can be updated
                "risk_factors": risk_factors,
                "address_confidence": 0.0,
                "intent_verified": False,
                "payment_status": "COD",
                "active_agent": "orchestrator",
                "interaction_count": 0,
                "discount_offered": 0.0,
                "final_disposition": None,
                "messages": []
            }
        }
        logger.info("session_created", phone=phone, session_id=session_id, order_id=order_id)
        return session_id

    @staticmethod
    def get_session(phone: str) -> Optional[Dict[str, Any]]:
        """Retrieve an active session by phone number."""
        return _SESSIONS.get(phone)

    @staticmethod
    def update_session_state(phone: str, new_state: Dict[str, Any]):
        """Update the LangGraph state for a session."""
        if phone in _SESSIONS:
            _SESSIONS[phone]["state"] = new_state
            logger.info("session_state_updated", phone=phone)

    @staticmethod
    def clear_session(phone: str):
        """End a session."""
        if phone in _SESSIONS:
            del _SESSIONS[phone]
            logger.info("session_cleared", phone=phone)
