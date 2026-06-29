"""
Intent Verification Agent.
Confirms genuine purchase intent and verifies physical availability / cash readiness.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage
from langgraph.prebuilt import ToolNode

from agents.state import MAVVEState
from agents.llm import get_llm
from agents.tools.sentiment_analyzer import analyze_intent_sentiment
from config import settings

logger = structlog.get_logger()

# ── 1. LLM & Tools Setup ─────────────────────────────────

INTENT_TOOLS = [analyze_intent_sentiment]

llm = get_llm()

llm_with_tools = llm.bind_tools(INTENT_TOOLS)

# ── 2. System Prompts ────────────────────────────────────

INTENT_SYSTEM_PROMPT = """
You are the MAVVE Intent Verification Agent.
Your goal is to gently confirm that the user actually intended to place this Cash-on-Delivery (COD) order and is ready to receive it.

You speak empathetically and simply in the customer's preferred language: {language}.

Instructions:
1. Review the conversation history. If this is the first message, politely ask: 
   "Hi, we received an order for ₹{total_amount}. Just confirming you placed this and have the cash ready for delivery in the next 2-3 days?"
2. When the user replies, ALWAYS use the `analyze_intent_sentiment` tool to evaluate their response.
3. Handle Edge Cases based on sentiment:
   - "hesitant" / "son ordered": Ask gently if they want to proceed or cancel without penalty.
   - "evasive" / "arrange money": State the exact delivery timeline. If they can't arrange it by then, offer to pause or cancel.
   - "hostile" / "cancel": Acknowledge immediately and say the order is cancelled (no pressure).
   - "confident" / "yes": Thank them warmly and confirm dispatch.
4. Keep all responses to a single, short sentence. No multi-paragraph explanations.
"""

# ── 3. Node Implementation ───────────────────────────────

def intent_agent_node(state: MAVVEState) -> MAVVEState:
    """
    Main entry for the Intent Verification Agent.
    Invokes the LLM, handles tool calls, and updates intent_verified in state.
    """
    logger.info("node_enter", node="intent_agent", order_id=state.get("order_id"))
    
    messages = state.get("messages", [])
    user_language = state.get("user_language", "hi")
    
    # Mock retrieving order total (in production, fetch from DB using order_id)
    total_amount = 499.0 
    
    sys_msg = SystemMessage(content=INTENT_SYSTEM_PROMPT.format(
        language=user_language, 
        total_amount=total_amount
    ))
    
    llm_messages = [sys_msg] + messages
    
    response = llm_with_tools.invoke(llm_messages)
    
    intent_verified = state.get("intent_verified", False)
    
    if response.tool_calls:
        logger.info("tool_calls_detected", calls=len(response.tool_calls))
        tool_messages = []
        for tool_call in response.tool_calls:
            if tool_call["name"] == "analyze_intent_sentiment":
                result = analyze_intent_sentiment.invoke(tool_call["args"])
                classification = result.get("classification")
                
                logger.info("intent_sentiment_analyzed", classification=classification)
                
                # Update intent state based on confident classification
                if classification == "confident":
                    intent_verified = True
                
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
                
        final_messages = llm_messages + [response] + tool_messages
        final_response = llm_with_tools.invoke(final_messages)
        
        new_messages = [response] + tool_messages + [final_response]
    else:
        new_messages = [response]
        
    return {
        "messages": new_messages,
        "active_agent": "intent_agent",
        "intent_verified": intent_verified,
        "interaction_count": state.get("interaction_count", 0) + 1
    }

# ── 4. Standalone Test ───────────────────────────────────
if __name__ == "__main__":
    print("--- Intent Verification Agent Simulation ---")
    
    scenarios = [
        ("Confident", "Haan bhai, main ghar par hi hu, bhej do."),
        ("Hesitant", "Meri beti ne galti se order kar diya hoga..."),
        ("Arranging Money", "Paisa kal aayega, kal bhej sakte ho kya?"),
        ("Hostile", "Cancel it right now. I didn't order this fake item.")
    ]
    
    for scenario_name, user_input in scenarios:
        print(f"\n\n{'='*40}")
        print(f"Scenario: {scenario_name}")
        print(f"{'='*40}")
        
        state: MAVVEState = {
            "order_id": "ORD-456",
            "user_id": "USR-1",
            "user_language": "English/Hinglish",
            "address_confidence": 0.9,
            "intent_verified": False,
            "payment_status": "COD",
            "active_agent": "intent_agent",
            "risk_factors": ["high_historical_rto"],
            "interaction_count": 0,
            "final_disposition": None,
            "messages": [HumanMessage(content=user_input)]
        }
        
        print("[User]:", state["messages"][0].content)
        
        new_state = intent_agent_node(state)
        
        print("\n[Agent output updates]:")
        for msg in new_state["messages"]:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    print("  Tool Calls:", [t["name"] for t in msg.tool_calls])
                elif msg.content:
                    print("  [Agent]:", msg.content)
            elif isinstance(msg, ToolMessage):
                print("  [Tool Result]:", msg.content)
                
        print("\n[Intent Verified State]:", new_state.get("intent_verified"))
