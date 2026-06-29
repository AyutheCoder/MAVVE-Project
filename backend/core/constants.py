"""
MAVVE constants — application-wide constant values.
"""

# ── Supported Languages ──────────────────────────────────
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "mr": "Marathi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
    "en": "English",
}

DEFAULT_LANGUAGE = "hi"

# ── Order Statuses ───────────────────────────────────────
class OrderStatus:
    PLACED = "PLACED"
    INTERCEPTED = "INTERCEPTED"
    VALIDATED = "VALIDATED"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    RTO = "RTO"
    CANCELLED = "CANCELLED"

# ── Payment Modes ────────────────────────────────────────
class PaymentMode:
    COD = "COD"
    PREPAID = "PREPAID"
    PREPAID_PENDING = "PREPAID_PENDING"

# ── Agent Types ──────────────────────────────────────────
class AgentType:
    ORCHESTRATOR = "orchestrator"
    ADDRESS = "address_resolution"
    INTENT = "intent_verification"
    PREPAID = "prepaid_conversion"

# ── Risk Factors ─────────────────────────────────────────
class RiskFactor:
    ADDRESS_ANOMALY = "address_anomaly"
    BEHAVIORAL = "behavioral"
    FRAUD_SIGNAL = "fraud_signal"
    HIGH_RTO_PINCODE = "high_rto_pincode"
    FIRST_ORDER = "first_order"
    HIGH_VALUE = "high_value"
    REPEAT_RTO = "repeat_rto"

# ── Conversation Outcomes ────────────────────────────────
class ConversationOutcome:
    CONVERTED = "converted"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"
    TIMED_OUT = "timed_out"

# ── Language Emoji Flags ─────────────────────────────────
LANGUAGE_FLAGS = {
    "hi": "🇮🇳",
    "mr": "🇮🇳",
    "bn": "🇮🇳",
    "ta": "🇮🇳",
    "te": "🇮🇳",
    "kn": "🇮🇳",
    "gu": "🇮🇳",
    "ml": "🇮🇳",
    "pa": "🇮🇳",
    "en": "🇬🇧",
}
