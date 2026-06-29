"""
Order Updater Tool.
Updates order payment status and triggers dispatch workflows.
"""

from typing import Dict, Any
from langchain_core.tools import tool
import structlog

logger = structlog.get_logger()

@tool
def confirm_prepaid_conversion(order_id: str, new_amount: float, discount_applied: float) -> str:
    """
    Update the order in the database to reflect successful prepaid conversion,
    and trigger the warehouse dispatch signal.
    
    Args:
        order_id (str): The unique order identifier.
        new_amount (float): The final amount paid.
        discount_applied (float): The discount percentage applied (e.g. 5, 10, 15).
        
    Returns:
        String confirmation message.
    """
    logger.info(
        "prepaid_conversion_confirmed", 
        order_id=order_id, 
        amount=new_amount, 
        discount=discount_applied
    )
    
    # In a real app, this would execute an async SQLAlchemy update:
    # UPDATE orders SET payment_mode = 'PREPAID', total_amount = new_amount, status = 'VALIDATED' WHERE id = order_id
    
    return f"Success: Order {order_id} successfully converted to PREPAID with {discount_applied}% discount. Dispatch triggered."
