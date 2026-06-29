"""
Payment Link Tool.
Simulates generating Razorpay/UPI deep links and checking status.
"""

from typing import Dict, Any
from langchain_core.tools import tool
import structlog
import uuid
import time

logger = structlog.get_logger()

# Mock DB for payment links
_MOCK_PAYMENT_LINKS: Dict[str, Dict[str, Any]] = {}

@tool
def generate_payment_link(order_id: str, amount: float) -> Dict[str, Any]:
    """
    Generate a time-sensitive UPI deep link for an order.
    
    Args:
        order_id (str): The unique order identifier.
        amount (float): The final discounted amount to be paid.
        
    Returns:
        Dict containing 'payment_url', 'expires_in_minutes', and 'link_id'.
    """
    link_id = f"pay_{uuid.uuid4().hex[:8]}"
    payment_url = f"upi://pay?pa=mavve@ybl&pn=MAVVE&am={amount}&tr={order_id}"
    
    _MOCK_PAYMENT_LINKS[link_id] = {
        "order_id": order_id,
        "amount": amount,
        "status": "pending",
        "created_at": time.time()
    }
    
    logger.info("payment_link_generated", link_id=link_id, amount=amount, order_id=order_id)
    
    return {
        "link_id": link_id,
        "payment_url": payment_url,
        "expires_in_minutes": 15,
        "message": "Click the link to pay via GPay/PhonePe/Paytm."
    }

@tool
def check_payment_status(link_id: str) -> str:
    """
    Check the status of a previously generated payment link.
    
    Args:
        link_id (str): The payment link ID returned by generate_payment_link.
        
    Returns:
        String status: 'pending', 'success', 'failed', or 'expired'.
    """
    logger.info("check_payment_status_called", link_id=link_id)
    link = _MOCK_PAYMENT_LINKS.get(link_id)
    
    if not link:
        return "not_found"
        
    # For simulation, we randomly succeed 70% of the time if it's pending
    if link["status"] == "pending":
        import random
        if random.random() > 0.3:
            link["status"] = "success"
            
    return link["status"]
