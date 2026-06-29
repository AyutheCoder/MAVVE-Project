"""
MAVVE custom exceptions.
"""


class MAVVEException(Exception):
    """Base exception for all MAVVE errors."""
    def __init__(self, message: str, code: str = "MAVVE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class OrderNotFoundError(MAVVEException):
    """Raised when an order is not found."""
    def __init__(self, order_id: str):
        super().__init__(f"Order not found: {order_id}", code="ORDER_NOT_FOUND")


class SessionNotFoundError(MAVVEException):
    """Raised when a MAVVE session is not found."""
    def __init__(self, session_id: str):
        super().__init__(f"Session not found: {session_id}", code="SESSION_NOT_FOUND")


class AgentExecutionError(MAVVEException):
    """Raised when an agent fails during execution."""
    def __init__(self, agent_type: str, detail: str):
        super().__init__(
            f"Agent '{agent_type}' execution failed: {detail}",
            code="AGENT_EXECUTION_ERROR",
        )


class BhashiniServiceError(MAVVEException):
    """Raised when Bhashini API call fails."""
    def __init__(self, detail: str):
        super().__init__(f"Bhashini service error: {detail}", code="BHASHINI_ERROR")


class WhatsAppServiceError(MAVVEException):
    """Raised when WhatsApp API call fails."""
    def __init__(self, detail: str):
        super().__init__(f"WhatsApp service error: {detail}", code="WHATSAPP_ERROR")


class PaymentServiceError(MAVVEException):
    """Raised when payment gateway operation fails."""
    def __init__(self, detail: str):
        super().__init__(f"Payment service error: {detail}", code="PAYMENT_ERROR")
