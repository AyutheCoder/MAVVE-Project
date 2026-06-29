"""
Payment gateway integration service (Razorpay).
Handles UPI payment link generation and verification.
Placeholder — full implementation in Prompt 7.
"""

import structlog

logger = structlog.get_logger()


class PaymentService:
    """
    Integrates with Razorpay for dynamic UPI payment link generation.
    Used by the Prepaid Conversion Agent to incentivize COD→Prepaid transitions.
    """

    def __init__(self, key_id: str = None, key_secret: str = None):
        self.key_id = key_id
        self.key_secret = key_secret
        logger.info("payment_service_initialized")

    async def generate_upi_link(self, order_id: str, amount: float, expiry_minutes: int = 15) -> dict:
        """Generate a UPI payment link. Full implementation in Prompt 7."""
        return {
            "payment_link_id": "mock_link_id",
            "short_url": f"https://rzp.io/mock/{order_id}",
            "amount": amount,
            "expires_at": None,
        }

    async def verify_payment(self, payment_id: str) -> dict:
        """Verify a payment. Full implementation in Prompt 7."""
        return {"status": "mock_verified", "payment_id": payment_id}
