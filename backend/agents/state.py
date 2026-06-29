from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class MAVVEState(TypedDict):
    """
    Core state object for the MAVVE LangGraph Orchestrator.
    This holds the conversational context and decision metadata across all agents.
    """
    messages: Annotated[List[AnyMessage], add_messages]
    
    order_id: str
    user_id: str
    user_language: str              # ISO 639-1 code (e.g., "hi", "mr", "bn")
    
    # Agent specific states
    address_confidence: float       # 0.0 - 1.0
    intent_verified: bool
    payment_status: str             # "COD" | "PREPAID_PENDING" | "PREPAID_SUCCESS"
    discount_offered: float         # Max discount authorized/offered (₹)
    
    # Routing and Metadata
    active_agent: str               # "orchestrator" | "address" | "intent" | "prepaid"
    risk_factors: List[str]         # e.g., ["address_anomaly", "high_value_cod"]
    interaction_count: int          # Number of exchange rounds
    final_disposition: Optional[str] # "DISPATCH" | "CANCEL" | "ESCALATE"
