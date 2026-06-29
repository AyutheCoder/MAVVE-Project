"""
Address Resolution Agent.
Analyzes vague rural Indian addresses and engages in interactive dialogue 
to resolve missing components using landmarks.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage
from langgraph.prebuilt import ToolNode

from agents.state import MAVVEState
from agents.llm import get_llm
from agents.tools.geo_lookup import geo_lookup
from agents.tools.address_normalizer import address_normalizer
from config import settings

logger = structlog.get_logger()

# ── 1. LLM & Tools Setup ─────────────────────────────────

ADDRESS_TOOLS = [geo_lookup, address_normalizer]

llm = get_llm()

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(ADDRESS_TOOLS)


# ── 2. System Prompts ────────────────────────────────────

ADDRESS_SYSTEM_PROMPT = """
You are the MAVVE Address Resolution Agent. 
Your goal is to clarify vague, incomplete, or ambiguous addresses provided by rural Indian customers for their e-commerce deliveries.

You speak empathetically and simply in the customer's preferred language: {language}.

Instructions:
1. Analyze the conversation history and the user's latest response.
2. If you need to understand the local area better, use the `geo_lookup` tool with the user's pincode.
3. If the user provides new address details, use the `address_normalizer` tool to parse it and get a confidence score.
4. If the confidence score is still below 0.85, ask a single, very simple clarifying question (e.g., "Is there a temple or school near your house?").
5. Do NOT overwhelm the user with multiple questions. Be extremely polite and reassuring.
6. If the confidence score is >= 0.85, thank the user and confirm their order will be dispatched to the refined address.

Remember: Many customers in rural areas don't have house numbers or street names. Focus on identifying prominent local landmarks, nearby shops, or major roads.
"""


# ── 3. Node Implementation ───────────────────────────────

def address_agent_node(state: MAVVEState) -> MAVVEState:
    """
    Main entry for the Address Resolution Agent.
    Invokes the LLM, handles tool calls, and updates confidence in state.
    """
    logger.info("node_enter", node="address_agent", order_id=state.get("order_id"))
    
    messages = state.get("messages", [])
    user_language = state.get("user_language", "hi")
    
    # 1. Format the system prompt with current state
    sys_msg = SystemMessage(content=ADDRESS_SYSTEM_PROMPT.format(language=user_language))
    
    # We prefix our system prompt to the message history for the LLM
    llm_messages = [sys_msg] + messages
    
    # 2. Call the LLM
    response = llm_with_tools.invoke(llm_messages)
    
    # 3. Handle Tool Calls
    confidence = state.get("address_confidence", 0.0)
    
    if response.tool_calls:
        logger.info("tool_calls_detected", calls=len(response.tool_calls))
        # Execute tools manually for simplicity in this node
        tool_messages = []
        for tool_call in response.tool_calls:
            if tool_call["name"] == "geo_lookup":
                result = geo_lookup.invoke(tool_call["args"])
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
            elif tool_call["name"] == "address_normalizer":
                result = address_normalizer.invoke(tool_call["args"])
                # Extract confidence from result and update state
                confidence = float(result.get("confidence_score", confidence))
                logger.info("address_confidence_updated", new_score=confidence)
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
                
        # Send tool results back to LLM to get final message
        final_messages = llm_messages + [response] + tool_messages
        final_response = llm_with_tools.invoke(final_messages)
        
        # Append only the agent's final message to the global state
        new_messages = [response] + tool_messages + [final_response]
    else:
        new_messages = [response]
        
    return {
        "messages": new_messages,
        "active_agent": "address_agent",
        "address_confidence": confidence,
        "interaction_count": state.get("interaction_count", 0) + 1
    }

# ── 4. Standalone Test ───────────────────────────────────
if __name__ == "__main__":
    print("--- Address Resolution Agent Simulation ---")
    
    # Mock state
    state: MAVVEState = {
        "order_id": "ORD-123",
        "user_id": "USR-1",
        "user_language": "English (but use simple terms)",
        "address_confidence": 0.3,
        "intent_verified": False,
        "payment_status": "COD",
        "active_agent": "address_agent",
        "risk_factors": ["address_anomaly"],
        "interaction_count": 0,
        "final_disposition": None,
        "messages": [
            HumanMessage(content="Near big temple, Dist Nashik. Pincode: 422001")
        ]
    }
    
    print("\n[User]:", state["messages"][0].content)
    
    # Run Node
    new_state = address_agent_node(state)
    
    print("\n[Agent output updates]:")
    for msg in new_state["messages"]:
        if isinstance(msg, AIMessage):
            if msg.tool_calls:
                print("  Tool Calls:", [t["name"] for t in msg.tool_calls])
            elif msg.content:
                print("  [Agent]:", msg.content)
        elif isinstance(msg, ToolMessage):
            print("  [Tool Result]:", msg.content)
            
    print("\n[New Address Confidence]:", new_state.get("address_confidence"))
    print("[Interaction Count]:", new_state.get("interaction_count"))
